import tkinter as tk

from student import Student
from teacher import Teacher
from course import Course
from enrollment import Enrollment
from fees import Fees
from university import UniversityError
from gui_common import CONTENT_BG, HEADING_FG, FONT


class DashboardPage(tk.Frame):
    """Plain-text statistics, no icons."""

    def __init__(self, parent):
        super().__init__(parent, bg=CONTENT_BG)
        tk.Label(self, text="Dashboard", font=(FONT, 22, "bold"),
                 bg=CONTENT_BG, fg=HEADING_FG).pack(anchor="w", padx=25, pady=(20, 10))
        try:
            self.show_stats()
        except UniversityError as err:
            tk.Label(self, text=f"Could not load statistics.\n{err}", justify="left",
                     bg=CONTENT_BG, fg="firebrick", font=(FONT, 12)).pack(anchor="w", padx=25)

    def section(self, heading, lines):
        tk.Label(self, text=heading, font=(FONT, 14, "bold"), bg=CONTENT_BG,
                 fg=HEADING_FG).pack(anchor="w", padx=25, pady=(14, 2))
        for line in lines:
            tk.Label(self, text=line, font=(FONT, 12), bg=CONTENT_BG
                     ).pack(anchor="w", padx=40)

    def show_stats(self):
        fee = Fees().summary()
        self.section("Student Details", [f"Students: {Student().count()}"])
        self.section("Teacher Info", [f"Teachers: {Teacher().count()}",
                                      f"Departments: {Teacher().department_count()}"])
        self.section("Course Info", [f"Courses: {Course().count()}"])
        self.section("Enrollment Info", [f"Enrollments: {Enrollment().count()}"])
        self.section("Fee Info", [
            f"Fee records: {fee['records']}",
            f"Paid: {fee['paid']}",
            f"Pending: {fee['pending']}",
            f"Partial: {fee['partial']}",
            f"Overdue: {fee['overdue']}",
            f"Total amount due: {fee['total']}",
            f"Paid amount: {fee['paid_amount']}",
            f"Outstanding amount: {fee['outstanding']}",
        ])
