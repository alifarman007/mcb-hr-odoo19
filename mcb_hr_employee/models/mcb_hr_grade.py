from odoo import api, fields, models


class McbHrGrade(models.Model):
    _name = "mcb.hr.grade"
    _description = "MCB Salary Grade"
    _order = "sequence, code"
    _rec_name = "display_name"

    code = fields.Char(string="Grade Code", required=True, help="e.g. G1, G6, G10")
    name = fields.Char(string="Grade Name", required=True, help="e.g. Senior Manager, Officer, Driver")
    sequence = fields.Integer(default=10)
    band = fields.Selection([
        ("senior", "Senior (Grade 1–5)"),
        ("mid", "Mid-level (Grade 6–8)"),
        ("support", "Support / Driver (Grade 9–10)"),
    ], required=True, default="mid")
    description = fields.Text()
    active = fields.Boolean(default=True)

    overtime_eligible = fields.Boolean(
        string="OT eligible",
        help="SRS PAY-003 — only Support Staff & Drivers are eligible for overtime.",
    )
    travel_entitlement = fields.Char(
        string="Travel Entitlement",
        help="Free-text description (e.g. AC Chair / Air Economy).",
    )
    annual_leave_days = fields.Integer(
        string="Annual Leave (days/yr)",
        default=18,
        help="Default annual leave entitlement for this grade.",
    )

    display_name = fields.Char(compute="_compute_display_name", store=True)

    _code_unique = models.Constraint(
        "unique(code)",
        "Grade code must be unique.",
    )

    @api.depends("code", "name")
    def _compute_display_name(self):
        for rec in self:
            rec.display_name = f"{rec.code or ''} — {rec.name or ''}".strip(" —")
