from university import UniversityManagement, UniversityError


class Student(UniversityManagement):

    def count(self):
        return self.count_rows("students")

    def get_all(self):
        return self.fetch_all(
            "SELECT Student_ID, Student_Name, Email, Admission_date "
            "FROM students ORDER BY Student_ID")

    def get_by_id(self, student_id):
        sid = self.to_int(student_id, "Student ID")
        return self.fetch_one(
            "SELECT Student_ID, Student_Name, Email, Admission_date "
            "FROM students WHERE Student_ID=%s", (sid,))

    def exists(self, student_id):
        return self.get_by_id(student_id) is not None

    def add(self, student_id, name, email, admission_date):
        sid = self.to_int(student_id, "Student ID", minimum=1)
        name = self.require_text(name, "Name")
        email = self.check_email(email)
        self.check_length("students", "Student_Name", name, "Name")
        self.check_length("students", "Email", email, "Email")
        admission_date = self.to_date(admission_date, "Admission date")
        if self.exists(sid):
            raise UniversityError("A student with this ID already exists.")
        self.execute(
            "INSERT INTO students (Student_ID, Student_Name, Email, Admission_date) "
            "VALUES (%s, %s, %s, %s)", (sid, name, email, admission_date))

    def update(self, student_id, name, email, admission_date):
        sid = self.to_int(student_id, "Student ID")
        name = self.require_text(name, "Name")
        email = self.check_email(email)
        self.check_length("students", "Student_Name", name, "Name")
        self.check_length("students", "Email", email, "Email")
        admission_date = self.to_date(admission_date, "Admission date")
        if not self.exists(sid):
            raise UniversityError("No student with this ID exists.")
        self.execute(
            "UPDATE students SET Student_Name=%s, Email=%s, Admission_date=%s "
            "WHERE Student_ID=%s", (name, email, admission_date, sid))

    def delete(self, student_id):
        sid = self.to_int(student_id, "Student ID")
        if not self.exists(sid):
            raise UniversityError("No student with this ID exists.")
        # remove the student's linked records first, all in one transaction
        self.execute_many([
            ("DELETE FROM Fees WHERE Student_ID=%s", (sid,)),
            ("DELETE FROM Enrollment WHERE Student_ID=%s", (sid,)),
            ("DELETE FROM students WHERE Student_ID=%s", (sid,)),
        ])
