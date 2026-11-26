from university import UniversityManagement, UniversityError
from teacher import Teacher


class Course(UniversityManagement):

    def count(self):
        return self.count_rows("course")

    def get_all(self):
        return self.fetch_all(
            "SELECT c.Course_ID, c.Course_Name, c.Credit_Hrs, c.Teacher_ID, t.Teacher_Name "
            "FROM course c LEFT JOIN Teacher t ON c.Teacher_ID = t.Teacher_ID "
            "ORDER BY c.Course_ID")

    def get_by_id(self, course_id):
        cid = self.to_int(course_id, "Course ID")
        return self.fetch_one(
            "SELECT Course_ID, Course_Name, Credit_Hrs, Teacher_ID "
            "FROM course WHERE Course_ID=%s", (cid,))

    def exists(self, course_id):
        return self.get_by_id(course_id) is not None

    def _dept_of(self, teacher_id):
        """A course belongs to its teacher's department."""
        if teacher_id is None:
            return None
        row = self.fetch_one("SELECT Dept_no FROM Teacher WHERE Teacher_ID=%s", (teacher_id,))
        return row[0] if row else None

    def _teacher_or_none(self, teacher_id):
        if str(teacher_id).strip() == "":
            return None
        tid = self.to_int(teacher_id, "Teacher ID")
        if not Teacher().exists(tid):
            raise UniversityError("No teacher with that ID exists.")
        return tid

    def add(self, course_id, name, credit_hours, teacher_id=""):
        cid = self.to_int(course_id, "Course ID", minimum=1)
        name = self.require_text(name, "Course name")
        self.check_length("course", "Course_Name", name, "Course name")
        credits = self.to_amount(credit_hours, "Credit hours")
        tid = self._teacher_or_none(teacher_id)
        if self.exists(cid):
            raise UniversityError("A course with this ID already exists.")
        self.execute(
            "INSERT INTO course (Course_ID, Course_Name, Dept_no, Teacher_ID, Credit_Hrs) "
            "VALUES (%s, %s, %s, %s, %s)", (cid, name, self._dept_of(tid), tid, credits))

    def update(self, course_id, name, credit_hours, teacher_id=""):
        cid = self.to_int(course_id, "Course ID")
        name = self.require_text(name, "Course name")
        self.check_length("course", "Course_Name", name, "Course name")
        credits = self.to_amount(credit_hours, "Credit hours")
        tid = self._teacher_or_none(teacher_id)
        if not self.exists(cid):
            raise UniversityError("No course with this ID exists.")
        self.execute(
            "UPDATE course SET Course_Name=%s, Credit_Hrs=%s, Teacher_ID=%s, Dept_no=%s "
            "WHERE Course_ID=%s", (name, credits, tid, self._dept_of(tid), cid))

    def delete(self, course_id):
        cid = self.to_int(course_id, "Course ID")
        if not self.exists(cid):
            raise UniversityError("No course with this ID exists.")
        self.execute_many([
            ("DELETE FROM Enrollment WHERE Course_ID=%s", (cid,)),
            ("DELETE FROM course WHERE Course_ID=%s", (cid,)),
        ])
