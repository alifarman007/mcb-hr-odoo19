from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    # TAX-006 (+ client feedback: TIN as well as BIN)
    mcb_bin_no = fields.Char(
        string="BIN (Business Identification No)",
        help="TAX-006 — vendor BIN used to validate VAT applicability.",
    )
    mcb_tin_no = fields.Char(
        string="TIN (Taxpayer Identification No)",
        help="TAX-006 feedback — TIN for income-tax/TDS validation.",
    )
