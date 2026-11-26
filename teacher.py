from university import UniversityManagement, UniversityError


class Teacher(UniversityManagement):

    def count(self):
        return self.count_rows("Teacher")

    def department_count(self):
        return self.count_rows("Department")

    def get_all(self):
        return self.fetch_all(
            "SELECT t.Teacher_ID, t.Teacher_Name, t.Salary, t.Dept_no, d.Dept_Name "
            "FROM Teacher t LEFT JOIN Department d ON t.Dept_no = d.Dept_no "
            "ORDER BY t.Teacher_ID")

    def get_by_id(self, teacher_id):
        tid = self.to_int(teacher_id, "Teacher ID")
        return self.fetch_one(
            "SELECT Teacher_ID, Teacher_Name, Salary, Dept_no "
            "FROM Teacher WHERE Teacher_ID=%s", (tid,))

    def exists(self, teacher_id):
        return self.get_by_id(teacher_id) is not None

    def department_summary(self):
        """Departments with how many teachers each has (from your first version)."""
        return self.fetch_all(
            "SELECT d.Dept_no, d.Dept_Name, COUNT(t.Teacher_ID) "
            "FROM Department d LEFT JOIN Teacher t ON d.Dept_no = t.Dept_no "
            "GROUP BY d.Dept_no, d.Dept_Name")

    def _check_department(self, dept_no):
        if self.fetch_one("SELECT 1 FROM Department WHERE Dept_no=%s", (dept_no,)) is None:
            raise UniversityError("That department number does not exist.")

    def add(self, teacher_id, name, salary, dept_no):
        tid = self.to_int(teacher_id, "Teacher ID", minimum=1)
        name = self.require_text(name, "Name")
        self.check_length("Teacher", "Teacher_Name", name, "Name")
        salary = self.to_int(salary, "Salary", minimum=0)
        dept_no = self.to_int(dept_no, "Department number")
        if self.exists(tid):
            raise UniversityError("A teacher with this ID already exists.")
        self._check_department(dept_no)
        self.execute(
            "INSERT INTO Teacher (Teacher_ID, Teacher_Name, Salary, Dept_no) "
            "VALUES (%s, %s, %s, %s)", (tid, name, salary, dept_no))

    def update(self, teacher_id, name, salary, dept_no):
        tid = self.to_int(teacher_id, "Teacher ID")
        name = self.require_text(name, "Name")
        self.check_length("Teacher", "Teacher_Name", name, "Name")
        salary = self.to_int(salary, "Salary", minimum=0)
        dept_no = self.to_int(dept_no, "Department number")
        if not self.exists(tid):
            raise UniversityError("No teacher with this ID exists.")
        self._check_department(dept_no)
        self.execute(
            "UPDATE Teacher SET Teacher_Name=%s, Salary=%s, Dept_no=%s "
            "WHERE Teacher_ID=%s", (name, salary, dept_no, tid))

    def delete(self, teacher_id):
        tid = self.to_int(teacher_id, "Teacher ID")
        if not self.exists(tid):
            raise UniversityError("No teacher with this ID exists.")
        # courses keep existing, they just lose their teacher
        self.execute_many([
            ("UPDATE course SET Teacher_ID=NULL WHERE Teacher_ID=%s", (tid,)),
            ("DELETE FROM Teacher WHERE Teacher_ID=%s", (tid,)),
        ])
