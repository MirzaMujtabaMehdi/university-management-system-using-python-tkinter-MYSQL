from gui_common import CrudPage
from teacher import Teacher


class TeacherPage(CrudPage):
    model_class = Teacher
    title = "Teachers"
    fields = [("id", "Teacher ID"), ("name", "Name"), ("salary", "Salary"),
              ("dept", "Department Number")]
    columns = [("Teacher ID", 90), ("Name", 200), ("Salary", 100),
               ("Dept No", 80), ("Department", 200)]
    delete_warning = "Courses taught by this teacher will stay, but with no teacher."

    def do_add(self, v):
        self.model.add(v["id"], v["name"], v["salary"], v["dept"])
        return "Teacher added."

    def do_update(self, v):
        self.model.update(v["id"], v["name"], v["salary"], v["dept"])
        return "Teacher updated."

    def do_delete(self, v):
        self.model.delete(v["id"])
        return "Teacher deleted."
