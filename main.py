import tkinter as tk
from tkinter import messagebox

from university import UniversityManagement, UniversityError
from gui_common import CONTENT_BG
from gui_sidebar import Sidebar
from gui_dashboard import DashboardPage
from gui_students import StudentPage
from gui_teachers import TeacherPage
from gui_courses import CoursePage
from gui_enrollment import EnrollmentPage
from gui_fees import FeesPage, FeeStatusPage

PAGES = {
    "students": StudentPage,
    "teachers": TeacherPage,
    "courses": CoursePage,
    "enrollment": EnrollmentPage,
    "fees": FeesPage,
}


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("University Management System")
        self.geometry("1150x680")
        self.minsize(950, 550)
        self.sidebar = Sidebar(self, self.show_page)       # left
        self.sidebar.pack(side="left", fill="y")
        self.content = tk.Frame(self, bg=CONTENT_BG)        # right
        self.content.pack(side="right", fill="both", expand=True)
        self.current_page = None

        self.sidebar.select("dashboard", None)              # dashboard is the default

    def show_page(self, section, action):
        try:
            if section == "dashboard":
                page = DashboardPage(self.content)
            elif section == "fees" and action == "status":
                page = FeeStatusPage(self.content)
            else:
                page = PAGES[section](self.content, action)
        except UniversityError as err:
            messagebox.showerror("Database problem", str(err))
            return
        if self.current_page is not None:
            self.current_page.destroy()
        page.pack(fill="both", expand=True)
        self.current_page = page


def main():
    try:
        UniversityManagement().create_tables()
    except UniversityError as err:
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror("Database problem", str(err))
        return
    App().mainloop()


if __name__ == "__main__":
    main()
