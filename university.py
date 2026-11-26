import re
from datetime import datetime

import mysql.connector
from mysql.connector import Error

# Database settings - change these if your MySQL setup changes.
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "Mirza123*",
    "database": "practice_db1",
}


class UniversityError(Exception):
    """Any problem we want to show to the user in plain words."""


class UniversityManagement:
    """Parent class. Holds the shared database connection, the query helpers
    and the input checks. Student, Teacher, Fees, Course and Enrollment
    all inherit from this."""

    TABLES = ("students", "Teacher", "Department", "course", "Enrollment", "Fees")
    _connection = None  # one connection shared by every child class

    def __init__(self):
        self._get_connection()

    # ---------------- connection ----------------
    @staticmethod
    def _get_connection():
        conn = UniversityManagement._connection
        try:
            if conn is None or not conn.is_connected():
                conn = mysql.connector.connect(**DB_CONFIG, autocommit=True)
                UniversityManagement._connection = conn
            return conn
        except Error as err:
            raise UniversityError(UniversityManagement._friendly(err))

    @staticmethod
    def _friendly(err):
        """Turn a MySQL error into a sentence a normal user understands."""
        code = getattr(err, "errno", None)
        text = getattr(err, "msg", None) or str(err)
        if code == 1062:
            return "That ID (or record) already exists."
        if code in (1451, 1452):
            return "This record is linked to other records, so the change was blocked."
        if code == 1406:
            found = re.search(r"column '([^']+)'", text)
            where = f"the {found.group(1)} column" if found else "a column"
            return f"The value is too long for {where}."
        if code in (1264, 1265, 1292, 1366, 1411, 1525):
            return "A value has the wrong type or is out of range for its column."
        if code in (1048, 1364):
            return "A required value is missing."
        if code == 1054:
            return f"The program expects a column your table does not have: {text}"
        if code == 1146:
            return f"A table is missing in the database: {text}"
        if code == 1064:
            return f"The SQL statement is not valid: {text}"
        if code in (1142, 1143, 1044):
            return "Your MySQL user does not have permission for this action."
        if code == 1045:
            return "MySQL rejected the username or password. Check DB_CONFIG at the top of university.py."
        if code == 1049:
            return "The database name in DB_CONFIG (university.py) does not exist."
        if code in (1205, 1213):
            return "The database is busy (locked). Please try again."
        if code in (2002, 2003):
            return "Cannot reach the MySQL server. Is it running?"
        if code in (2006, 2013, 2055):
            return "The connection to MySQL was lost. Please try again."
        return f"Database error: {text}"

    # ---------------- running queries ----------------
    def fetch_all(self, query, params=None):
        cursor = None
        try:
            cursor = self._get_connection().cursor()
            cursor.execute(query, params or ())
            return cursor.fetchall()
        except Error as err:
            raise UniversityError(self._friendly(err))
        except (TypeError, ValueError) as err:
            raise UniversityError(f"A value had the wrong data type: {err}")
        finally:
            if cursor:
                cursor.close()

    def fetch_one(self, query, params=None):
        cursor = None
        try:
            cursor = self._get_connection().cursor()
            cursor.execute(query, params or ())
            return cursor.fetchone()
        except Error as err:
            raise UniversityError(self._friendly(err))
        except (TypeError, ValueError) as err:
            raise UniversityError(f"A value had the wrong data type: {err}")
        finally:
            if cursor:
                cursor.close()

    def execute(self, query, params=None):
        return self.execute_many([(query, params)])

    def execute_many(self, statements):
        """Run several statements as ONE transaction: all succeed or none do."""
        conn = self._get_connection()
        cursor = None
        try:
            conn.start_transaction()
            cursor = conn.cursor()
            affected = 0
            for query, params in statements:
                cursor.execute(query, params or ())
                affected = cursor.rowcount
            conn.commit()
            return affected
        except Error as err:
            try:
                conn.rollback()
            except Error:
                pass
            raise UniversityError(self._friendly(err))
        except (TypeError, ValueError) as err:
            try:
                conn.rollback()
            except Error:
                pass
            raise UniversityError(f"A value had the wrong data type: {err}")
        finally:
            if cursor:
                cursor.close()

    def count_rows(self, table):
        if table not in self.TABLES:
            raise UniversityError("Unknown table.")
        return self.fetch_one(f"SELECT COUNT(*) FROM {table}")[0]

    def create_tables(self):
        """Creates any table that does not exist yet. Existing tables and their
        rows are never dropped or changed, except that Enrollment gets a
        Course_ID column added if it does not have one (existing rows stay)."""
        self.execute_many([
            ("""CREATE TABLE IF NOT EXISTS Department (
                    Dept_no INT, Dept_Name VARCHAR(20), Location VARCHAR(20))""", None),
            ("""CREATE TABLE IF NOT EXISTS students (
                    Student_ID INT PRIMARY KEY, Student_Name VARCHAR(50),
                    Email VARCHAR(100), Admission_date DATE)""", None),
            ("""CREATE TABLE IF NOT EXISTS Teacher (
                    Teacher_ID INT PRIMARY KEY, Teacher_Name VARCHAR(50),
                    Salary INT, Dept_no INT)""", None),
            ("""CREATE TABLE IF NOT EXISTS course (
                    Course_ID INT, Course_Name VARCHAR(50), Dept_no INT,
                    Teacher_ID INT, Credit_Hrs DECIMAL(4,1))""", None),
            ("""CREATE TABLE IF NOT EXISTS Enrollment (
                    Enrollment_ID INT PRIMARY KEY, Student_ID INT,
                    enrollment_date DATE, Course_ID INT)""", None),
            ("""CREATE TABLE IF NOT EXISTS Fees (
                    Fee_ID INT PRIMARY KEY, Student_ID INT, amount_Due INT,
                    Due_Date DATE,
                    payment_status ENUM('Paid','Pending','Partial'))""", None),
        ])
        has_course_id = self.fetch_one(
            "SELECT 1 FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA=DATABASE() "
            "AND LOWER(TABLE_NAME)='enrollment' AND LOWER(COLUMN_NAME)='course_id'")
        if has_course_id is None:
            self.execute("ALTER TABLE Enrollment ADD COLUMN Course_ID INT NULL")

    def next_id(self, table, column):
        """Next free ID for tables whose ID column is not AUTO_INCREMENT."""
        if table not in self.TABLES:
            raise UniversityError("Unknown table.")
        return (self.fetch_one(f"SELECT COALESCE(MAX({column}), 0) FROM {table}")[0]) + 1

    # ---------------- input checks ----------------
    _lengths = {}   # remembers each column's maximum length

    def check_length(self, table, column, value, label):
        """Stop text that is longer than the column allows BEFORE MySQL complains."""
        key = (table.lower(), column.lower())
        if key not in UniversityManagement._lengths:
            row = self.fetch_one(
                "SELECT CHARACTER_MAXIMUM_LENGTH FROM INFORMATION_SCHEMA.COLUMNS "
                "WHERE TABLE_SCHEMA=DATABASE() AND LOWER(TABLE_NAME)=%s AND LOWER(COLUMN_NAME)=%s",
                key)
            UniversityManagement._lengths[key] = row[0] if row else None
        limit = UniversityManagement._lengths[key]
        if limit and len(value) > limit:
            raise UniversityError(
                f"{label} is too long ({len(value)} characters). "
                f"The database column allows only {limit}.")
        return value

    @staticmethod
    def require_text(value, label):
        value = (value or "").strip()
        if not value:
            raise UniversityError(f"{label} cannot be empty.")
        return value

    @staticmethod
    def to_int(value, label, minimum=None):
        try:
            number = int(str(value).strip())
        except ValueError:
            raise UniversityError(f"{label} must be a whole number.")
        if minimum is not None and number < minimum:
            raise UniversityError(f"{label} must be at least {minimum}.")
        return number

    @staticmethod
    def to_amount(value, label):
        try:
            amount = round(float(str(value).strip()), 2)
        except ValueError:
            raise UniversityError(f"{label} must be a number.")
        if amount < 0:
            raise UniversityError(f"{label} cannot be negative.")
        return amount

    @staticmethod
    def to_date(value, label):
        try:
            return datetime.strptime(str(value).strip(), "%Y-%m-%d").strftime("%Y-%m-%d")
        except ValueError:
            raise UniversityError(f"{label} must look like 2026-09-01 (YYYY-MM-DD).")

    @staticmethod
    def check_email(value):
        value = UniversityManagement.require_text(value, "Email")
        if not re.match(r"^[^@\s]+@[^@\s]+$", value):
            raise UniversityError("Email must look like name@something (no spaces, one @).")
        return value
