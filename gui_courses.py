from gui_common import CrudPage
from course import Course


class CoursePage(CrudPage):
    model_class = Course
    title = "Courses"
    fields = [("id", "Course ID"), ("name", "Course Name"), ("credits", "Credit Hours"),
              ("teacher", "Teacher ID (optional)")]
    columns = [("Course ID", 90), ("Course Name", 220), ("Credit Hours", 100),
               ("Teacher ID", 90), ("Teacher", 200)]
    delete_warning = "This also removes every enrollment in this course."

    def do_add(self, v):
        self.model.add(v["id"], v["name"], v["credits"], v["teacher"])
        return "Course added."

    def do_update(self, v):
        self.model.update(v["id"], v["name"], v["credits"], v["teacher"])
        return "Course updated."

    def do_delete(self, v):
        self.model.delete(v["id"])
        return "Course removed."
