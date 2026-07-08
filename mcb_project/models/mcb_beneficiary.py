from odoo import api, fields, models


class McbBeneficiaryEntry(models.Model):
    """MON-005 (Must) — beneficiary reach per activity per period, disaggregated."""
    _name = "mcb.beneficiary.entry"
    _description = "MCB Beneficiary Data Entry"
    _order = "date desc"

    project_id = fields.Many2one("project.project", required=True, index=True)
    task_id = fields.Many2one("project.task", string="Activity / Task",
                              domain="[('project_id', '=', project_id)]")
    date = fields.Date(required=True, default=fields.Date.context_today,
                       string="Reporting Date")
    beneficiary_type = fields.Selection([
        ("direct", "Direct"), ("indirect", "Indirect"),
    ], default="direct", required=True)
    male = fields.Integer()
    female = fields.Integer()
    other = fields.Integer(string="Other / Undisclosed")
    children = fields.Integer(string="Children (<18)")
    adults = fields.Integer(string="Adults (18–59)")
    elderly = fields.Integer(string="Elderly (60+)")
    location_type = fields.Selection([
        ("camp", "Camp (FDMN)"), ("host", "Host Community"),
    ], default="camp", required=True)
    camp_no = fields.Char(string="Camp / Union")
    total = fields.Integer(compute="_compute_total", store=True)
    note = fields.Char()

    @api.depends("male", "female", "other")
    def _compute_total(self):
        for rec in self:
            rec.total = rec.male + rec.female + rec.other
