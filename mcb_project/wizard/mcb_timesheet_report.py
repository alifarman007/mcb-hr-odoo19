from dateutil.relativedelta import relativedelta

from odoo import api, fields, models


class McbTimesheetReportWizard(models.TransientModel):
    """Annexure-23 — Time Sheet of Individual Staff with 'At a Glance'
    policy-vs-actual project split (TMS-001/002/006)."""
    _name = "mcb.timesheet.report.wizard"
    _inherit = ["mcb.xlsx.mixin"]
    _description = "Individual Staff Timesheet (Annexure-23)"

    employee_id = fields.Many2one("hr.employee", required=True)
    month_date = fields.Date(
        required=True, default=lambda s: fields.Date.context_today(s).replace(day=1))

    def _period(self):
        start = self.month_date.replace(day=1)
        return start, start + relativedelta(months=1, days=-1)

    def _day_rows(self):
        start, end = self._period()
        ts_lines = self.env["account.analytic.line"].search([
            ("employee_id", "=", self.employee_id.id),
            ("project_id", "!=", False),
            ("date", ">=", start), ("date", "<=", end)])
        attendance = self.env["hr.attendance"].search([
            ("employee_id", "=", self.employee_id.id),
            ("check_in", ">=", fields.Datetime.to_datetime(start)),
            ("check_in", "<=", fields.Datetime.to_datetime(end).replace(hour=23, minute=59))])
        leaves = self.env["hr.leave"].search([
            ("employee_id", "=", self.employee_id.id),
            ("state", "=", "validate"),
            ("date_from", "<=", fields.Datetime.to_datetime(end)),
            ("date_to", ">=", fields.Datetime.to_datetime(start))])
        projects = ts_lines.mapped("project_id")
        rows, cur = [], start
        while cur <= end:
            att = attendance.filtered(lambda a: a.check_in.date() == cur)
            on_leave = any(l.date_from.date() <= cur <= l.date_to.date() for l in leaves)
            day_lines = ts_lines.filtered(lambda l: l.date == cur)
            per_project = {p: sum(day_lines.filtered(
                lambda l: l.project_id == p).mapped("unit_amount")) for p in projects}
            rows.append({
                "date": cur,
                "day": cur.strftime("%a"),
                "status": ("Leave" if on_leave else
                           "Weekend" if cur.weekday() in (4, 5) else "Working"),
                "in_time": min(att.mapped("check_in")).strftime("%H:%M") if att else "",
                "out_time": (max(att.mapped("check_out")).strftime("%H:%M")
                             if att and all(att.mapped("check_out")) else ""),
                "per_project": per_project,
                "total": sum(day_lines.mapped("unit_amount")),
            })
            cur += relativedelta(days=1)
        return projects, rows

    def _glance(self, projects, rows):
        start, end = self._period()
        total_hours = sum(r["total"] for r in rows)
        actual = {p: sum(r["per_project"].get(p, 0.0) for r in rows) for p in projects}
        assignments = self.env["mcb.project.assignment"].search([
            ("employee_id", "=", self.employee_id.id),
            ("date_from", "<=", end), ("date_to", ">=", start)])
        policy = {a.project_id: a.percent for a in assignments}
        return {
            "total_hours": total_hours,
            "working_days": len([r for r in rows if r["status"] == "Working"]),
            "actual_pct": {p: (actual[p] / total_hours * 100.0) if total_hours else 0.0
                           for p in projects},
            "policy_pct": policy,
        }

    def action_print_pdf(self):
        return self.env.ref("mcb_project.action_report_mcb_timesheet").report_action(self)

    def action_export_xlsx(self):
        projects, rows = self._day_rows()
        headers = ["Date", "Day", "Day Status", "In", "Out"] + \
                  [p.name for p in projects] + ["Total Hours"]
        data = []
        for r in rows:
            data.append([str(r["date"]), r["day"], r["status"], r["in_time"],
                         r["out_time"]]
                        + [round(r["per_project"].get(p, 0.0), 1) for p in projects]
                        + [round(r["total"], 1)])
        return self._mcb_xlsx_download(
            f"timesheet_{self.employee_id.name}_{self.month_date:%Y_%m}.xlsx",
            "Individual Timesheet", headers, data)
