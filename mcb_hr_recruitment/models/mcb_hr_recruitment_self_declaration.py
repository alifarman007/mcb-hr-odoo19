from odoo import fields, models


class McbHrRecruitmentSelfDeclaration(models.Model):
    """REC-013 — Self-Declaration of Conflict of Interest for RC members."""
    _name = "mcb.hr.recruitment.self.declaration"
    _description = "MCB Recruitment Self-Declaration"
    _inherit = ["mail.thread"]
    _order = "create_date desc"

    requisition_id = fields.Many2one("mcb.hr.staff.requisition", required=True, ondelete="cascade")
    rc_member_id = fields.Many2one("res.users", string="RC Member", required=True, default=lambda s: s.env.user)
    declaration_date = fields.Date(default=fields.Date.context_today, required=True)
    relationship_disclosed = fields.Selection([
        ("none", "No relationship with any candidate"),
        ("family", "Family relation disclosed"),
        ("business", "Business / financial interest disclosed"),
        ("other", "Other"),
    ], default="none", required=True)
    details = fields.Text()
    signed = fields.Boolean(string="Signed", default=False)
