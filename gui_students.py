from gui_common import CrudPage
from student import Student


class StudentPage(CrudPage):
    model_class = Student
    title = "Students"
    fields = [("id", "Student ID"), ("name", "Name"), ("email", "Email"),
              ("admission", "Admission Date (YYYY-MM-DD)")]
    columns = [("Student ID", 90), ("Name", 200), ("Email", 250), ("Admission Date", 130)]
    delete_warning = "This also removes the student's fee records and enrollments."

    def do_add(self, v):
        self.model.add(v["id"], v["name"], v["email"], v["admission"])
        return "Student added."

    def do_update(self, v):
        self.model.update(v["id"], v["name"], v["email"], v["admission"])
        return "Student updated."

    def do_delete(self, v):
        self.model.delete(v["id"])
        return "Student deleted."
