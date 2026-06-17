from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    mcb_pf_employee_pct = fields.Float(
        string="PF Employee Contribution (%)", default=10.0,
        help="SRS PAY-005 — Provident Fund employee share.",
    )
    mcb_pf_employer_pct = fields.Float(
        string="PF Employer Contribution (%)", default=10.0,
        help="SRS PAY-005 — Provident Fund employer matching share.",
    )
    mcb_baishakhi_pct = fields.Float(
        string="Baishakhi Bonus (% basic)", default=20.0,
        help="SRS PAY-004 — Baishakhi festival bonus percentage of basic.",
    )
    mcb_festival_bonus_count = fields.Integer(
        string="Annual Festival Bonus Count", default=2,
        help="SRS PAY-004 — number of festival bonuses per year (typically 2 Eids).",
    )
    mcb_gratuity_threshold_years = fields.Float(
        string="Gratuity Threshold (years)", default=10.0,
        help="SRS PAY-006 — service years after which gratuity = 45 days/yr; below = 30 days/yr.",
    )
    mcb_gratuity_deposit_month = fields.Integer(
        string="Gratuity Deposit Month", default=6,
        help="SRS PAY-006 (v2 feedback) — month (1-12) in which the full year's "
             "gratuity is deposited to the Gratuity Fund. Default 6 = June "
             "(end of the Bangladesh fiscal year). Deposited yearly, not monthly.",
    )
