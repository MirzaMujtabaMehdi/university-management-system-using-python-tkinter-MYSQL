from gui_common import CrudPage
from enrollment import Enrollment


class EnrollmentPage(CrudPage):
    model_class = Enrollment
    title = "Enrollment"
    fields = [("id", "Enrollment ID"), ("student", "Student ID"), ("course", "Course ID")]
    columns = [("Enrollment ID", 100), ("Student ID", 90), ("Course ID", 90),
               ("Student", 200), ("Course", 200), ("Enrolled On", 110)]
    hidden_in_add = ("id",)   # the database numbers enrollments itself

    def do_add(self, v):
        self.model.add(v["student"], v["course"])
        return "Student enrolled in the course."

    def do_update(self, v):
        self.model.update(v["id"], v["student"], v["course"])
        return "Enrollment updated."

    def do_delete(self, v):
        self.model.delete(v["id"])
        return "Enrollment removed."
