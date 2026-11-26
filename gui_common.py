import tkinter as tk
from tkinter import ttk, messagebox

from university import UniversityError

# Plain named colors only
MENU_BG = "navy"
SUBMENU_BG = "midnightblue"
MENU_FG = "white"
ACTIVE_BG = "steelblue"
CONTENT_BG = "white"
FORM_BG = "whitesmoke"
HEADING_FG = "navy"
ADD_COLOR = "seagreen"
UPDATE_COLOR = "darkorange"
DELETE_COLOR = "firebrick"
CLEAR_COLOR = "gray"
FONT = "Arial"

MODE_TITLES = {"view": "View All", "add": "Add", "update": "Update", "delete": "Delete"}


def make_table(parent, columns):
    """columns = [(heading, width), ...]  ->  (frame, treeview)"""
    frame = tk.Frame(parent, bg=CONTENT_BG)
    ids = [f"c{i}" for i in range(len(columns))]
    tree = ttk.Treeview(frame, columns=ids, show="headings")
    for col_id, (heading, width) in zip(ids, columns):
        tree.heading(col_id, text=heading)
        tree.column(col_id, width=width, anchor="w")
    scroll = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=scroll.set)
    tree.pack(side="left", fill="both", expand=True)
    scroll.pack(side="right", fill="y")
    return frame, tree


def fill_table(tree, rows):
    tree.delete(*tree.get_children())
    for row in rows:
        tree.insert("", "end", values=["" if v is None else v for v in row])


class CrudPage(tk.Frame):
    """One page = a heading, an optional form, and a table of all records.
    Each entity (students, teachers...) subclasses this and fills in the details."""

    model_class = None      # e.g. Student
    title = ""
    fields = []             # [(key, label), ...]  first one is the ID field
    columns = []            # [(heading, width), ...]
    hidden_in_add = ()      # keys the database generates itself
    delete_warning = ""

    def __init__(self, parent, mode):
        super().__init__(parent, bg=CONTENT_BG)
        self.mode = mode
        self.model = self.model_class()
        self.entries = {}

        tk.Label(self, text=f"{self.title} - {MODE_TITLES[mode]}",
                 font=(FONT, 18, "bold"), bg=CONTENT_BG, fg=HEADING_FG
                 ).pack(anchor="w", padx=20, pady=(15, 5))

        if mode != "view":
            self.build_form()

        frame, self.tree = make_table(self, self.columns)
        frame.pack(fill="both", expand=True, padx=20, pady=(10, 20))
        self.tree.bind("<<TreeviewSelect>>", self.on_row_click)
        self.refresh_table()

    # ---------- form ----------
    def visible_fields(self):
        if self.mode == "add":
            return [f for f in self.fields if f[0] not in self.hidden_in_add]
        if self.mode == "delete":
            return self.fields[:1]
        return self.fields

    def build_form(self):
        form = tk.Frame(self, bg=FORM_BG, padx=15, pady=10)
        form.pack(fill="x", padx=20, pady=5)

        for row, (key, label) in enumerate(self.visible_fields()):
            tk.Label(form, text=label, bg=FORM_BG, font=(FONT, 10)
                     ).grid(row=row, column=0, sticky="w", pady=3, padx=(0, 15))
            entry = tk.Entry(form, width=38, font=(FONT, 10))
            entry.grid(row=row, column=1, sticky="w", pady=3)
            self.entries[key] = entry

        buttons = tk.Frame(form, bg=FORM_BG)
        buttons.grid(row=len(self.entries), column=0, columnspan=2, sticky="w", pady=(10, 0))
        text, color = {"add": ("Add", ADD_COLOR),
                       "update": ("Update", UPDATE_COLOR),
                       "delete": ("Delete", DELETE_COLOR)}[self.mode]
        tk.Button(buttons, text=text, bg=color, fg="white", width=10,
                  command=self.run_action).pack(side="left", padx=(0, 8))
        tk.Button(buttons, text="Clear", bg=CLEAR_COLOR, fg="white", width=10,
                  command=self.clear_form).pack(side="left")

        if self.mode in ("update", "delete"):
            tk.Label(form, text="Tip: click a row in the table to fill the form.",
                     bg=FORM_BG, fg="gray30", font=(FONT, 9)
                     ).grid(row=len(self.entries) + 1, column=0, columnspan=2, sticky="w", pady=(8, 0))

    def clear_form(self):
        for entry in self.entries.values():
            entry.delete(0, "end")

    def on_row_click(self, event):
        selected = self.tree.selection()
        if not selected or self.mode not in ("update", "delete"):
            return
        row = self.tree.item(selected[0])["values"]
        data = dict(zip([f[0] for f in self.fields], row))
        for key, entry in self.entries.items():
            entry.delete(0, "end")
            entry.insert(0, data.get(key, ""))

    # ---------- actions ----------
    def run_action(self):
        values = {key: entry.get().strip() for key, entry in self.entries.items()}
        try:
            if self.mode == "add":
                message = self.do_add(values)
            elif self.mode == "update":
                message = self.do_update(values)
            else:
                id_key = self.fields[0][0]
                question = f"Delete {self.title.lower()} record {values[id_key]}?"
                if self.delete_warning:
                    question += "\n\n" + self.delete_warning
                if not messagebox.askyesno("Please confirm", question):
                    return
                message = self.do_delete(values)
        except UniversityError as err:
            messagebox.showwarning("Cannot complete", str(err))
            return
        except Exception as err:  # anything we did not expect
            messagebox.showerror("Unexpected error", str(err))
            return
        messagebox.showinfo("Done", message)
        self.clear_form()
        self.refresh_table()

    def refresh_table(self):
        try:
            fill_table(self.tree, self.load_rows())
        except UniversityError as err:
            messagebox.showwarning("Cannot load data", str(err))

    # ---------- subclasses override these ----------
    def load_rows(self):
        return self.model.get_all()

    def do_add(self, v):
        raise NotImplementedError

    def do_update(self, v):
        raise NotImplementedError

    def do_delete(self, v):
        raise NotImplementedError
