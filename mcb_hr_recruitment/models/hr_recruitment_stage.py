from odoo import fields, models


class HrRecruitmentStage(models.Model):
    _inherit = "hr.recruitment.stage"

    mcb_stage_code = fields.Selection([
        ("requisition", "1 — New / Requisition"),
        ("approved", "2 — Approved"),
        ("published", "3 — Published"),
        ("received", "4 — Application Received"),
        ("shortlist", "5 — Shortlisted"),
        ("admit_card", "6 — Admit Card Issued"),
        ("written", "7 — Written Test"),
        ("oral", "8 — Oral Test"),
        ("merit", "9 — Merit Review"),
        ("hired", "10 — Offer / Hired"),
    ], string="MCB Stage Code", help="Map this stage to MCB SRS §4.3.")
