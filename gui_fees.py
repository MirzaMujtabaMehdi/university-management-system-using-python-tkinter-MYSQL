import tkinter as tk
from tkinter import messagebox

from fees import Fees
from university import UniversityError
from gui_common import (CrudPage, make_table, fill_table, CONTENT_BG, FORM_BG,
                        HEADING_FG, ADD_COLOR, CLEAR_COLOR, FONT)

FEE_COLUMNS = [("Fee ID", 70), ("Student ID", 90), ("Amount Due", 110),
               ("Due Date", 100), ("Status", 90), ("Student", 180)]


class FeesPage(CrudPage):
    model_class = Fees
    title = "Fees"
    fields = [("id", "Fee ID"), ("student", "Student ID"), ("amount", "Amount Due"),
              ("due", "Due Date (YYYY-MM-DD)"), ("status", "Status (Paid / Pending / Partial)")]
    columns = FEE_COLUMNS
    hidden_in_add = ("id",)

    def do_add(self, v):
        self.model.add(v["student"], v["amount"], v["due"], v["status"])
        return "Fee record added."

    def do_update(self, v):
        self.model.update(v["id"], v["student"], v["amount"], v["due"], v["status"])
        return "Fee record updated."

    def do_delete(self, v):
        self.model.delete(v["id"])
        return "Fee record deleted."


class FeeStatusPage(tk.Frame):
    """Check one student's fee status, or list everyone."""

    def __init__(self, parent):
        super().__init__(parent, bg=CONTENT_BG)
        self.fees = Fees()

        tk.Label(self, text="Fees - Check Status", font=(FONT, 18, "bold"),
                 bg=CONTENT_BG, fg=HEADING_FG).pack(anchor="w", padx=20, pady=(15, 5))

        top = tk.Frame(self, bg=FORM_BG, padx=15, pady=10)
        top.pack(fill="x", padx=20, pady=5)
        tk.Label(top, text="Student ID", bg=FORM_BG, font=(FONT, 10)).pack(side="left", padx=(0, 10))
        self.id_entry = tk.Entry(top, width=15, font=(FONT, 10))
        self.id_entry.pack(side="left", padx=(0, 10))
        tk.Button(top, text="Check", bg=ADD_COLOR, fg="white", width=10,
                  command=self.check).pack(side="left", padx=(0, 8))
        tk.Button(top, text="Show All", bg=CLEAR_COLOR, fg="white", width=10,
                  command=self.show_all).pack(side="left")

        self.result = tk.Label(self, text="", justify="left", anchor="w",
                               bg=CONTENT_BG, font=(FONT, 11))
        self.result.pack(fill="x", padx=20, pady=5)

        frame, self.tree = make_table(self, FEE_COLUMNS)
        frame.pack(fill="both", expand=True, padx=20, pady=(5, 20))
        self.show_all()

    def show_all(self):
        self.result.config(text="")
        try:
            fill_table(self.tree, self.fees.get_all())
        except UniversityError as err:
            messagebox.showwarning("Cannot load data", str(err))

    def check(self):
        try:
            info = self.fees.get_student_fees(self.id_entry.get())
        except UniversityError as err:
            messagebox.showwarning("Cannot check", str(err))
            return
        except Exception as err:
            messagebox.showerror("Unexpected error", str(err))
            return

        if not info["records"]:
            overall = "No fee records for this student."
        elif info["outstanding"] == 0:
            overall = "All fees are paid."
        elif info["overdue"]:
            overall = f"Fees are pending, {info['overdue']} record(s) past the due date."
        else:
            overall = "Fees are still pending."
        self.result.config(text=(
            f"Student: {info['name']} (ID {info['id']})\n"
            f"Total due: {info['total']}    Paid: {info['paid']}    "
            f"Still outstanding: {info['outstanding']}\n{overall}"))
        fill_table(self.tree, info["records"])
