from odoo import fields, models


class McbHrExitInterview(models.Model):
    """SEP-003 — Exit Interview form."""
    _name = "mcb.hr.exit.interview"
    _description = "MCB Exit Interview"
    _inherit = ["mail.thread"]
    _order = "interview_date desc"

    employee_id = fields.Many2one("hr.employee", required=True, ondelete="cascade")
    resignation_id = fields.Many2one("mcb.hr.resignation")
    interview_date = fields.Date(default=fields.Date.context_today)
    interviewer_id = fields.Many2one("res.users", default=lambda s: s.env.user)

    reason_overall = fields.Selection([
        ("better_offer", "Better job offer"),
        ("career_change", "Career change"),
        ("family", "Family / personal"),
        ("relocation", "Relocation"),
        ("dissatisfaction", "Dissatisfaction"),
        ("retirement", "Retirement"),
        ("other", "Other"),
    ], string="Primary reason for leaving", required=True, default="other")

    workplace_rating = fields.Selection([
        ("1", "1 — Poor"),
        ("2", "2"),
        ("3", "3 — Average"),
        ("4", "4"),
        ("5", "5 — Excellent"),
    ], string="Overall workplace rating")
    management_rating = fields.Selection([
        ("1", "1 — Poor"),
        ("2", "2"),
        ("3", "3 — Average"),
        ("4", "4"),
        ("5", "5 — Excellent"),
    ], string="Line-management rating")
    would_recommend = fields.Boolean(string="Would recommend MCB as employer?")
    suggestions = fields.Html(string="Suggestions for MCB")
    confidential_notes = fields.Html(string="Confidential HR Notes", groups="hr.group_hr_user")
