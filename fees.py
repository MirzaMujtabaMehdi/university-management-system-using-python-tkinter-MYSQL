from datetime import date

from university import UniversityManagement, UniversityError
from student import Student

STATUSES = ("Paid", "Pending", "Partial")


class Fees(UniversityManagement):
    """Works with your Fees table: Fee_ID, Student_ID, amount_Due, Due_Date, payment_status."""

    def count(self):
        return self.count_rows("Fees")

    def get_all(self):
        return self.fetch_all(
            "SELECT f.Fee_ID, f.Student_ID, f.amount_Due, f.Due_Date, f.payment_status, s.Student_Name "
            "FROM Fees f LEFT JOIN students s ON f.Student_ID = s.Student_ID "
            "ORDER BY f.Fee_ID")

    def get_by_id(self, fee_id):
        fid = self.to_int(fee_id, "Fee ID")
        return self.fetch_one(
            "SELECT Fee_ID, Student_ID, amount_Due, Due_Date, payment_status "
            "FROM Fees WHERE Fee_ID=%s", (fid,))

    @staticmethod
    def check_status(value):
        for status in STATUSES:
            if str(value).strip().lower() == status.lower():
                return status
        raise UniversityError("Status must be Paid, Pending or Partial.")

    def _checked(self, student_id, amount, due_date, status):
        sid = self.to_int(student_id, "Student ID")
        amount = self.to_int(amount, "Amount due", minimum=1)
        due_date = self.to_date(due_date, "Due date")
        status = self.check_status(status)
        if not Student().exists(sid):
            raise UniversityError("No student with that ID exists.")
        return sid, amount, due_date, status

    def add(self, student_id, amount, due_date, status):
        sid, amount, due_date, status = self._checked(student_id, amount, due_date, status)
        self.execute(
            "INSERT INTO Fees (Fee_ID, Student_ID, amount_Due, Due_Date, payment_status) "
            "VALUES (%s, %s, %s, %s, %s)",
            (self.next_id("Fees", "Fee_ID"), sid, amount, due_date, status))

    def update(self, fee_id, student_id, amount, due_date, status):
        fid = self.to_int(fee_id, "Fee ID")
        sid, amount, due_date, status = self._checked(student_id, amount, due_date, status)
        if self.get_by_id(fid) is None:
            raise UniversityError("No fee record with this ID exists.")
        self.execute(
            "UPDATE Fees SET Student_ID=%s, amount_Due=%s, Due_Date=%s, payment_status=%s "
            "WHERE Fee_ID=%s", (sid, amount, due_date, status, fid))

    def delete(self, fee_id):
        fid = self.to_int(fee_id, "Fee ID")
        if self.get_by_id(fid) is None:
            raise UniversityError("No fee record with this ID exists.")
        self.execute("DELETE FROM Fees WHERE Fee_ID=%s", (fid,))

    @staticmethod
    def is_overdue(status, due_date):
        return status != "Paid" and isinstance(due_date, date) and due_date < date.today()

    def get_student_fees(self, student_id):
        """One student's fee records plus totals (the 'check fee status' feature)."""
        sid = self.to_int(student_id, "Student ID")
        student = Student().get_by_id(sid)
        if student is None:
            raise UniversityError("No student with that ID exists.")
        rows = self.fetch_all(
            "SELECT Fee_ID, Student_ID, amount_Due, Due_Date, payment_status "
            "FROM Fees WHERE Student_ID=%s ORDER BY Fee_ID", (sid,))
        records = [row + (student[1],) for row in rows]
        return {
            "id": sid, "name": student[1], "records": records,
            "total": sum(r[2] for r in rows),
            "paid": sum(r[2] for r in rows if r[4] == "Paid"),
            "outstanding": sum(r[2] for r in rows if r[4] != "Paid"),
            "overdue": sum(1 for r in rows if self.is_overdue(r[4], r[3])),
        }

    def summary(self):
        rows = self.get_all()
        return {
            "records": len(rows),
            "paid": sum(1 for r in rows if r[4] == "Paid"),
            "pending": sum(1 for r in rows if r[4] == "Pending"),
            "partial": sum(1 for r in rows if r[4] == "Partial"),
            "overdue": sum(1 for r in rows if self.is_overdue(r[4], r[3])),
            "total": sum(r[2] for r in rows),
            "paid_amount": sum(r[2] for r in rows if r[4] == "Paid"),
            "outstanding": sum(r[2] for r in rows if r[4] != "Paid"),
        }
