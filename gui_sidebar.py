import tkinter as tk

from gui_common import MENU_BG, SUBMENU_BG, MENU_FG, ACTIVE_BG, FONT

CRUD = [("View All", "view"), ("Add", "add"), ("Delete", "delete"), ("Update", "update")]

# (heading, section key, submenu items)
MENU = [
    ("Students", "students", CRUD),
    ("Teachers", "teachers", CRUD),
    ("Fees", "fees", CRUD + [("Check Status", "status")]),
    ("Enrollment", "enrollment", CRUD),
    ("Courses", "courses", CRUD),
]


class Sidebar(tk.Frame):
    """Left menu. Headings open/close their submenu; the chosen item is highlighted."""

    def __init__(self, parent, on_select):
        super().__init__(parent, bg=MENU_BG, width=210)
        self.pack_propagate(False)
        self.on_select = on_select
        self.labels = {}      # (section, action) -> label
        self.base_bg = {}     # (section, action) -> normal background
        self.headers = {}     # section -> heading label
        self.submenus = {}    # section -> frame holding its items
        self.is_open = {}     # section -> True/False
        self.active = None

        tk.Label(self, text="University DBMS", bg=MENU_BG, fg=MENU_FG,
                 font=(FONT, 14, "bold")).pack(pady=(20, 15))

        self._item(self, "Dashboard", ("dashboard", None), MENU_BG)

        for heading, section, items in MENU:
            header = tk.Label(self, text=f"{heading}   +", bg=MENU_BG, fg=MENU_FG,
                              font=(FONT, 11, "bold"), anchor="w", padx=15, pady=8,
                              cursor="hand2")
            header.pack(fill="x")
            header.bind("<Button-1>", lambda e, s=section: self.toggle(s))
            self.headers[section] = header
            self.is_open[section] = False

            sub = tk.Frame(self, bg=SUBMENU_BG)
            self.submenus[section] = sub
            for text, action in items:
                self._item(sub, text, (section, action), SUBMENU_BG, indent=30)

    def _item(self, parent, text, key, bg, indent=15):
        label = tk.Label(parent, text=text, bg=bg, fg=MENU_FG, font=(FONT, 10),
                         anchor="w", padx=indent, pady=7, cursor="hand2")
        label.pack(fill="x")
        label.bind("<Button-1>", lambda e, k=key: self.select(*k))
        self.labels[key] = label
        self.base_bg[key] = bg

    def toggle(self, section):
        heading = next(h for h, s, _ in MENU if s == section)
        if self.is_open[section]:
            self.submenus[section].pack_forget()
            self.headers[section].config(text=f"{heading}   +")
        else:
            self.submenus[section].pack(fill="x", after=self.headers[section])
            self.headers[section].config(text=f"{heading}   -")
        self.is_open[section] = not self.is_open[section]

    def select(self, section, action):
        key = (section, action)
        if self.active is not None:
            self.labels[self.active].config(bg=self.base_bg[self.active])
        self.labels[key].config(bg=ACTIVE_BG)
        self.active = key
        self.on_select(section, action)
