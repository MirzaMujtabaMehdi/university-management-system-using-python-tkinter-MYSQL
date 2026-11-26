UNIVERSITY MANAGEMENT SYSTEM  (Python + MySQL + tkinter)
=========================================================

HOW TO RUN
----------
1. Keep ALL .py files together in ONE folder (PyCharm project folder).
2. Install the MySQL driver once:   pip install mysql-connector-python
3. Open university.py and check DB_CONFIG at the top (host, user, password,
   database). It is set to your practice_db1 database.
4. Run main.py.

Note: the old error "No module named 'config'" happened because settings used
to live in a separate config.py that was not copied. DB_CONFIG is now inside
university.py, so there is no config.py any more.

YOUR EXISTING DATA IS SAFE
--------------------------
The program never drops or alters your tables. On start it only runs
"CREATE TABLE IF NOT EXISTS", so students, Teacher and Department keep all
their rows. It only adds three new tables: Course, Enrollment and Fees.
(Tested on a copy of the practice_db1 layout: rows were identical afterwards.)


FILE STRUCTURE (who inherits from whom)
---------------------------------------
UniversityManagement (university.py)      <- PARENT
    |-- Student     (student.py)
    |-- Teacher     (teacher.py)
    |-- Course      (course.py)
    |-- Enrollment  (enrollment.py)
    |-- Fees        (fees.py)

GUI:  main.py -> gui_sidebar.py, gui_dashboard.py, gui_common.py (CrudPage)
      gui_students.py, gui_teachers.py, gui_courses.py,
      gui_enrollment.py, gui_fees.py   (each page inherits CrudPage)


=========================================================
FILE-BY-FILE: FUNCTIONS, LOGIC AND WHY
=========================================================

---------------------------------------------------------
university.py   (parent class + database engine)
---------------------------------------------------------
LOGIC: Every child class needs the same things: a connection to MySQL, a way
to run queries safely, and checks for user input. Writing that once here
avoids repeating it in five files. This is the point of the parent class.
One connection is shared by all classes (stored in the class variable
_connection) so the program does not open a new connection per object.

User-defined:
  UniversityError          Our own exception type. Everything the user should
                           see in plain words is raised as this, and the GUI
                           catches it and shows a message box.
  _get_connection()        Returns the shared connection, reconnecting if it
                           was lost. Turns connection failures into messages.
  _friendly(err)           Converts MySQL error numbers (duplicate key,
                           wrong password, server down...) into readable text.
  fetch_all(query,params)  Runs a SELECT and returns all rows.
  fetch_one(query,params)  Runs a SELECT and returns one row (or None).
  execute(query,params)    Runs one INSERT/UPDATE/DELETE.
  execute_many(list)       Runs several statements as ONE transaction: all
                           succeed or all are undone (rollback). Used so
                           deleting a student cannot leave half-deleted data.
  count_rows(table)        COUNT(*) of a table, only for known table names.
  create_tables()          Creates the missing tables (never touches existing).
  require_text, to_int, to_amount, to_date, check_email
                           Input validators. They clean the text and raise
                           UniversityError with a clear message if wrong.

Built-in / library used and why:
  mysql.connector.connect  Opens the MySQL connection.
  conn.is_connected()      Checks whether the connection is still alive.
  conn.start_transaction() / commit() / rollback()
                           Make several statements behave as one unit.
  cursor.execute / fetchall / fetchone / rowcount / close
                           Run SQL and read results; close frees resources.
  %s placeholders          Values are passed separately from the SQL text so
                           MySQL treats them as data (prevents SQL injection).
  re.match                 Regular expression to check the email shape.
  datetime.strptime/strftime  Check a date is real and in YYYY-MM-DD form.
  int(), float(), round(), str(), strip(), getattr()
                           Convert/clean values; round keeps money to 2
                           decimals; getattr safely reads the MySQL error code.
  try / except / finally   Exception handling: catch errors, always close the
                           cursor in finally.
  staticmethod             Validators and _friendly do not need "self".

---------------------------------------------------------
student.py   (class Student)
---------------------------------------------------------
LOGIC: Validate input first, then check the database (duplicate or missing),
then run the query. Delete removes the student's Fees and Enrollment rows
first, inside one transaction, so no orphan records remain.
User-defined: count, get_all, get_by_id, exists, add, update, delete.
Built-in used: none special beyond parent helpers (tuples, SQL via parent).

---------------------------------------------------------
teacher.py   (class Teacher)
---------------------------------------------------------
LOGIC: Same pattern as Student. A teacher must belong to an existing
department (checked in _check_department). Deleting a teacher sets
Course.Teacher_ID to NULL first, so courses survive without a teacher.
User-defined: count, department_count, get_all (joined with Department name),
get_by_id, exists, department_summary (your original "teachers per
department" query, now a LEFT JOIN so empty departments show too),
_check_department, add, update, delete.

---------------------------------------------------------
course.py   (class Course)
---------------------------------------------------------
LOGIC: add/remove courses. Teacher ID is optional; if given it must exist
(_teacher_or_none). Deleting a course removes its enrollments first.
User-defined: count, get_all (joined with teacher name), get_by_id, exists,
_teacher_or_none, add, update, delete.

---------------------------------------------------------
enrollment.py   (class Enrollment)
---------------------------------------------------------
LOGIC: Links a student to a course. Before adding it checks the student and
course exist and that the pair is not already enrolled (_already_enrolled).
The ID is AUTO_INCREMENT so MySQL numbers enrollments.
User-defined: count, get_all, get_by_id, _already_enrolled, _check_links,
add, update, delete.
Built-in used: date.today() to stamp the enrollment date.

---------------------------------------------------------
fees.py   (class Fees)
---------------------------------------------------------
LOGIC: One row per fee record (a student can have several). Status is not
stored; it is calculated each time so it is always correct:
   paid >= total        -> Paid
   due date passed      -> Overdue
   some paid            -> Partial
   nothing paid         -> Unpaid
User-defined: status (static), count, get_all (adds the Status column),
get_by_id, _amounts (checks total>0 and paid<=total), add, update, delete,
get_student_fees (one student's totals + records: the "check fee status"
feature), summary (counts and money totals for the dashboard).
Built-in used: float() for money math, sum() with generator expressions to
total columns, isinstance() to be sure the due date is a real date,
date.today() to detect overdue.

---------------------------------------------------------
gui_common.py   (shared GUI pieces)
---------------------------------------------------------
LOGIC: Students, teachers, courses, enrollment and fees all need the same
page: heading, form, buttons, table. CrudPage builds it once; each entity
page only lists its fields/columns and calls its model. Modes: view, add,
update, delete decide which form fields and button appear.
Colors are plain names (navy, steelblue, seagreen...) as requested.
User-defined: make_table, fill_table, and class CrudPage with
visible_fields, build_form, clear_form, on_row_click, run_action,
refresh_table, plus hooks load_rows/do_add/do_update/do_delete that child
pages override.
Built-in/library used: tkinter Frame, Label, Entry, Button; ttk.Treeview
(the table) and ttk.Scrollbar; messagebox (info/warning/error/yes-no
confirm); grid()/pack() for layout; dict(zip()) to map a clicked table row
to the form fields; entry.get/insert/delete to read and write text boxes.
run_action catches UniversityError (friendly warning) and Exception (any
unexpected bug) so the window never crashes.

---------------------------------------------------------
gui_students.py / gui_teachers.py / gui_courses.py / gui_enrollment.py
---------------------------------------------------------
LOGIC: Each is a small CrudPage child: it names the model class, the form
fields, the table columns, and implements do_add/do_update/do_delete by
calling the matching model method and returning a success message.

---------------------------------------------------------
gui_fees.py
---------------------------------------------------------
FeesPage: same as the others for fees add/update/delete/view.
FeeStatusPage: type a student ID and press Check to see total, paid,
remaining and a one-line verdict plus that student's records; Show All lists
every fee record with its status.

---------------------------------------------------------
gui_dashboard.py
---------------------------------------------------------
LOGIC: On opening it asks each model for counts (students, teachers,
departments, courses, enrollments, fee summary) and shows them as plain text
under headings. If the database is down it shows the error instead of
crashing. Functions: section(), show_stats().

---------------------------------------------------------
gui_sidebar.py
---------------------------------------------------------
LOGIC: MENU lists the sections and their submenu items. Clicking a heading
calls toggle(), which shows/hides its submenu (pack with after=heading, or
pack_forget) and flips the "+"/"-" sign. Clicking an item calls select(),
which highlights it (steelblue) and tells main.py which page to show.
Functions: _item, toggle, select.
Labels are used instead of Buttons so colors look the same on every OS.

---------------------------------------------------------
main.py
---------------------------------------------------------
LOGIC: main() first creates missing tables; if the database is unreachable it
shows a message box instead of a traceback. App builds the left Sidebar and
the right content area, then selects "dashboard" so the dashboard is the
default view. show_page() destroys the old page and builds the new one from
the PAGES dictionary (section name -> page class).
Built-in used: tk.Tk().mainloop() (starts the window event loop),
pack(side=...) for the left/right layout, __name__ == "__main__" guard.


WHY BOTH BUILT-IN AND USER-DEFINED FUNCTIONS?
---------------------------------------------
Built-in functions (int, float, sum, round, strip, zip, isinstance...) do
small general jobs that Python already does reliably, so we do not rewrite
them. User-defined functions hold OUR rules (what a valid student is, how a
fee status is decided, how a delete cascades). Keeping rules in named
functions means each rule exists in one place, the GUI stays thin, and a
bug is fixed once.

WHY TRY/EXCEPT EVERYWHERE?
--------------------------
Databases and users both fail in normal ways: wrong ID, duplicate ID, bad
date, server not running. Each layer converts the failure into a
UniversityError with a plain message, and the GUI shows it in a message box
so the program keeps running.

NEEDS FOR LATER (not built yet)
-------------------------------
Department add/edit/delete screens (teachers need an existing department).


UPDATE - MATCHING YOUR REAL SQL FILE (Testing Database.sql)
-----------------------------------------------------------
The dashboard error ("Unknown column Total_Fee") happened because my first
version assumed a different Fees table. The code now uses YOUR columns:
  Fees:       Fee_ID, Student_ID, amount_Due, Due_Date, payment_status
              (Paid / Pending / Partial is stored; "Overdue" is calculated)
  course:     Course_ID, Course_Name, Dept_no, Teacher_ID, Credit_Hrs
              (table name is lowercase "course", like in your SQL)
  Enrollment: Enrollment_ID, Student_ID, enrollment_date
The Fees, course and Enrollment IDs are not AUTO_INCREMENT in your SQL, so
university.py has next_id() which uses MAX(id)+1.
Enrollment had no Course_ID, so a student could not be linked to a course.
On startup create_tables() ADDS that one column (existing 4 rows keep their
data, Course_ID is empty for them). Nothing else in your tables is changed.


UPDATE - COMPLETE EXCEPTION HANDLING
------------------------------------
- Email rule relaxed: it only needs name@something (your data uses abc@123).
- check_length() in university.py compares text with the real column size
  (for example Email is varchar(14)) and gives a clear message first.
- _friendly() now translates many MySQL errors: value too long, wrong data
  type / out of range, missing value, unknown column, bad SQL, missing table,
  no permission, locked database, lost connection, linked records, duplicates.
- Wrong Python types (TypeError / ValueError) are also turned into messages,
  and a failed multi-step change is rolled back.
