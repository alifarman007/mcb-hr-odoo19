from odoo import api, fields, models


class HrPayslip(models.Model):
    _inherit = "hr.payslip"

    mcb_donor = fields.Char(
        related="version_id.mcb_donor", store=True, readonly=True,
        string="Donor (MCB)",
    )
    mcb_analytic_code = fields.Char(
        related="version_id.mcb_analytic_code", store=True, readonly=True,
        string="Analytic Cost Code (MCB)",
    )
    mcb_grade_id = fields.Many2one(
        "mcb.hr.grade", related="version_id.mcb_grade_id",
        store=True, readonly=True, string="MCB Grade",
    )
