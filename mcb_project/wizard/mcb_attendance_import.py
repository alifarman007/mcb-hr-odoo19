import base64
import csv
import io

from odoo import fields, models, _
from odoo.exceptions import UserError


class McbAttendanceImportWizard(models.TransientModel):
    """ATT-004 — camp attendance sheet import: CSV with
    employee_code,date(YYYY-MM-DD),check_in(HH:MM),check_out(HH:MM)."""
    _name = "mcb.attendance.import.wizard"
    _description = "Camp Attendance CSV Import (ATT-004)"

    file_data = fields.Binary(required=True, string="CSV File")
    file_name = fields.Char()

    def action_import(self):
        self.ensure_one()
        try:
            content = base64.b64decode(self.file_data).decode("utf-8-sig")
        except Exception:
            raise UserError(_("Could not read the file — provide UTF-8 CSV."))
        reader = csv.DictReader(io.StringIO(content))
        required = {"employee_code", "date", "check_in", "check_out"}
        if not required.issubset(set(reader.fieldnames or [])):
            raise UserError(_(
                "CSV must have headers: employee_code, date, check_in, check_out."))
        created, skipped = 0, []
        for row in reader:
            emp = self.env["hr.employee"].search(
                ["|", ("mcb_employee_code", "=", row["employee_code"]),
                 ("name", "=", row["employee_code"])], limit=1)
            if not emp:
                skipped.append(row["employee_code"])
                continue
            self.env["hr.attendance"].create({
                "employee_id": emp.id,
                "check_in": f"{row['date']} {row['check_in']}:00",
                "check_out": f"{row['date']} {row['check_out']}:00",
            })
            created += 1
        message = _("%d attendance records imported.", created)
        if skipped:
            message += _(" Unknown employees skipped: %s", ", ".join(set(skipped)))
        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {"title": _("Attendance Import"), "message": message,
                       "type": "success" if not skipped else "warning"},
        }
