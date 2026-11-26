from datetime import date

from university import UniversityManagement, UniversityError
from student import Student
from course import Course


class Enrollment(UniversityManagement):

    def count(self):
        return self.count_rows("Enrollment")

    def get_all(self):
        return self.fetch_all(
            "SELECT e.Enrollment_ID, e.Student_ID, e.Course_ID, "
            "s.Student_Name, c.Course_Name, e.enrollment_date "
            "FROM Enrollment e "
            "LEFT JOIN students s ON e.Student_ID = s.Student_ID "
            "LEFT JOIN course c ON e.Course_ID = c.Course_ID "
            "ORDER BY e.Enrollment_ID")

    def get_by_id(self, enrollment_id):
        eid = self.to_int(enrollment_id, "Enrollment ID")
        return self.fetch_one(
            "SELECT Enrollment_ID, Student_ID, Course_ID FROM Enrollment "
            "WHERE Enrollment_ID=%s", (eid,))

    def _already_enrolled(self, sid, cid, ignore_id=None):
        row = self.fetch_one(
            "SELECT Enrollment_ID FROM Enrollment WHERE Student_ID=%s AND Course_ID=%s",
            (sid, cid))
        return row is not None and row[0] != ignore_id

    def _check_links(self, sid, cid):
        if not Student().exists(sid):
            raise UniversityError("No student with that ID exists.")
        if not Course().exists(cid):
            raise UniversityError("No course with that ID exists.")

    def add(self, student_id, course_id):
        sid = self.to_int(student_id, "Student ID")
        cid = self.to_int(course_id, "Course ID")
        self._check_links(sid, cid)
        if self._already_enrolled(sid, cid):
            raise UniversityError("This student is already enrolled in that course.")
        self.execute(
            "INSERT INTO Enrollment (Enrollment_ID, Student_ID, Course_ID, enrollment_date) "
            "VALUES (%s, %s, %s, %s)",
            (self.next_id("Enrollment", "Enrollment_ID"), sid, cid,
             date.today().strftime("%Y-%m-%d")))

    def update(self, enrollment_id, student_id, course_id):
        eid = self.to_int(enrollment_id, "Enrollment ID")
        sid = self.to_int(student_id, "Student ID")
        cid = self.to_int(course_id, "Course ID")
        if self.get_by_id(eid) is None:
            raise UniversityError("No enrollment with this ID exists.")
        self._check_links(sid, cid)
        if self._already_enrolled(sid, cid, ignore_id=eid):
            raise UniversityError("This student is already enrolled in that course.")
        self.execute(
            "UPDATE Enrollment SET Student_ID=%s, Course_ID=%s WHERE Enrollment_ID=%s",
            (sid, cid, eid))

    def delete(self, enrollment_id):
        eid = self.to_int(enrollment_id, "Enrollment ID")
        if self.get_by_id(eid) is None:
            raise UniversityError("No enrollment with this ID exists.")
        self.execute("DELETE FROM Enrollment WHERE Enrollment_ID=%s", (eid,))
