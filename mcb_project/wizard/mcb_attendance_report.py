from dateutil.relativedelta import relativedelta

from odoo import fields, models


class McbAttendanceReportWizard(models.TransientModel):
    """Annexure-20 — Monthly Staff Attendance Information (ATT-001/002)."""
    _name = "mcb.attendance.report.wizard"
    _inherit = ["mcb.xlsx.mixin"]
    _description = "Monthly Staff Attendance (Annexure-20)"

    month_date = fields.Date(
        required=True, default=lambda s: fields.Date.context_today(s).replace(day=1))
    department_id = fields.Many2one("hr.department", string="Department / Office")
    project_name = fields.Char(string="Name of Project / Office")
    funded_by = fields.Char()

    def _period(self):
        start = self.month_date.replace(day=1)
        return start, start + relativedelta(months=1, days=-1)

    def _calendar_counts(self):
        start, end = self._period()
        total_days = (end - start).days + 1
        holidays = len([d for d in range(total_days)
                        if (start + relativedelta(days=d)).weekday() in (4, 5)])
        return total_days, holidays, total_days - holidays

    def _leave_days(self, employee, start, end, name_part=None, paid=None):
        domain = [("employee_id", "=", employee.id), ("state", "=", "validate"),
                  ("date_from", "<=", fields.Datetime.to_datetime(end)),
                  ("date_to", ">=", fields.Datetime.to_datetime(start))]
        leaves = self.env["hr.leave"].search(domain)
        if name_part:
            leaves = leaves.filtered(
                lambda l: name_part.lower() in (l.holiday_status_id.name or "").lower())
        if paid is True:
            leaves = leaves.filtered(lambda l: not l.holiday_status_id.unpaid)
        if paid is False:
            leaves = leaves.filtered(lambda l: l.holiday_status_id.unpaid)
        return sum(leaves.mapped("number_of_days"))

    def _rows(self):
        start, end = self._period()
        total_days, holidays, working_days = self._calendar_counts()
        domain = [("company_id", "=", self.env.company.id)]
        if self.department_id:
            domain.append(("department_id", "=", self.department_id.id))
        rows = []
        for emp in self.env["hr.employee"].search(domain, order="name"):
            att_days = len(set(
                a.check_in.date() for a in self.env["hr.attendance"].search([
                    ("employee_id", "=", emp.id),
                    ("check_in", ">=", fields.Datetime.to_datetime(start)),
                    ("check_in", "<=", fields.Datetime.to_datetime(end).replace(
                        hour=23, minute=59))])))
            lv_paid = self._leave_days(emp, start, end, paid=True)
            lv_unpaid = self._leave_days(emp, start, end, paid=False)
            absent = max(working_days - att_days - lv_paid - lv_unpaid, 0)
            payable = working_days - lv_unpaid - absent + holidays
            rows.append({
                "emp": emp,
                "joining": emp.mcb_service_continuity_date or "",
                "el": self._leave_days(emp, start, end, name_part="annual"),
                "cl": self._leave_days(emp, start, end, name_part="casual"),
                "sl": self._leave_days(emp, start, end, name_part="sick"),
                "present": att_days,
                "leave_paid": lv_paid,
                "leave_unpaid": lv_unpaid,
                "absent": absent,
                "holidays": holidays,
                "total": total_days,
                "payable": payable,
            })
        return rows

    def action_print_pdf(self):
        return self.env.ref("mcb_project.action_report_mcb_attendance").report_action(self)

    def action_export_xlsx(self):
        rows = [[r["emp"].name, r["emp"].job_title or "", str(r["joining"]),
                 r["el"], r["cl"], r["sl"], r["present"], r["leave_paid"],
                 r["leave_unpaid"], r["absent"], r["holidays"], r["total"],
                 r["payable"]] for r in self._rows()]
        return self._mcb_xlsx_download(
            f"monthly_attendance_{self.month_date:%Y_%m}.xlsx",
            "Monthly Staff Attendance",
            ["Employee", "Designation", "Joining", "EL", "CL", "SL", "Present",
             "Leave w/ Pay", "Leave w/o Pay", "Absent", "Holidays", "Total Days",
             "Days Payable"],
            rows)
