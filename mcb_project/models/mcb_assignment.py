from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class McbProjectAssignment(models.Model):
    """PRJ-005 / TMS-002 — staff-to-project % time allocation per period."""
    _name = "mcb.project.assignment"
    _description = "MCB Project Staff Assignment (% time)"
    _order = "date_from desc"

    employee_id = fields.Many2one("hr.employee", required=True, index=True)
    project_id = fields.Many2one("project.project", required=True, index=True)
    analytic_account_id = fields.Many2one(
        related="project_id.account_id", store=True,
        string="Project Analytic")
    date_from = fields.Date(required=True,
                            default=lambda s: fields.Date.context_today(s).replace(day=1))
    date_to = fields.Date(required=True)
    percent = fields.Float(string="% Time", required=True, default=100.0)
    company_id = fields.Many2one("res.company", default=lambda s: s.env.company)

    @api.constrains("employee_id", "date_from", "date_to", "percent")
    def _check_total(self):
        for rec in self:
            if rec.percent <= 0 or rec.percent > 100:
                raise ValidationError(_("% time must be between 0 and 100."))
            if rec.date_to < rec.date_from:
                raise ValidationError(_("End date before start date."))
            overlaps = self.search([
                ("employee_id", "=", rec.employee_id.id),
                ("id", "!=", rec.id),
                ("date_from", "<=", rec.date_to),
                ("date_to", ">=", rec.date_from),
            ])
            if sum(overlaps.mapped("percent")) + rec.percent > 100.0001:
                raise ValidationError(_(
                    "PRJ-005 — %s would be allocated more than 100%% for the "
                    "overlapping period.", rec.employee_id.name))

    def name_get_percent(self):
        return f"{self.project_id.name} ({self.percent:g}%)"

    @api.model
    def _cron_autofill_timesheets(self):
        """TMS-003 — draft timesheet lines from yesterday's attendance, split
        across the employee's assigned projects by % (staff can then edit and
        submit in the native grid; supervisor validates → TMS-005)."""
        from datetime import timedelta
        yesterday = fields.Date.context_today(self) - timedelta(days=1)
        assignments = self.search([
            ("date_from", "<=", yesterday), ("date_to", ">=", yesterday)])
        Timesheet = self.env["account.analytic.line"]
        for emp in assignments.mapped("employee_id"):
            worked = sum(self.env["hr.attendance"].search([
                ("employee_id", "=", emp.id),
                ("check_in", ">=", fields.Datetime.to_datetime(yesterday)),
                ("check_in", "<", fields.Datetime.to_datetime(yesterday)
                 + timedelta(days=1)),
            ]).mapped("worked_hours"))
            if not worked:
                continue
            existing = Timesheet.search_count([
                ("employee_id", "=", emp.id), ("date", "=", yesterday),
                ("project_id", "!=", False)], limit=1)
            if existing:
                continue
            for a in assignments.filtered(lambda x: x.employee_id == emp):
                Timesheet.create({
                    "employee_id": emp.id,
                    "project_id": a.project_id.id,
                    "date": yesterday,
                    "name": "Auto from attendance (TMS-003)",
                    "unit_amount": round(worked * a.percent / 100.0, 2),
                })
