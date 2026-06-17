from odoo import api, fields, models


class HrVersion(models.Model):
    _inherit = "hr.version"

    # --- EMP-002 employment type ---
    mcb_employment_type = fields.Selection([
        ("permanent", "Permanent / Regular"),
        ("project", "Project / Contractual"),
        ("probationary", "Probationary"),
        ("support", "Support Staff / Driver"),
    ], string="MCB Employment Type", default="permanent", tracking=True, groups="hr.group_hr_user")

    # --- EMP-003 project / donor / analytic ---
    mcb_project_code = fields.Char(
        string="Project Code",
        groups="hr.group_hr_user",
        help="Short project code used as prefix for the employee code (e.g. MEAL, RRRC, FDMN).",
    )
    mcb_donor = fields.Char(
        string="Donor",
        groups="hr.group_hr_user",
        help="Donor agency funding this position (UNFPA, CARE, UNICEF, DFAT, ...).",
    )
    mcb_analytic_code = fields.Char(
        string="Analytic Cost Code",
        groups="hr.group_hr_user",
        help="Analytic / cost-center code for donor reporting.",
    )

    # --- EMP-004 grade ---
    mcb_grade_id = fields.Many2one(
        "mcb.hr.grade",
        string="MCB Grade",
        tracking=True,
        groups="hr.group_hr_user",
        help="Salary grade per SRS §3.3. Drives per-diem, OT eligibility, leave entitlement.",
    )
    mcb_grade_band = fields.Selection(
        related="mcb_grade_id.band", store=True, readonly=True, groups="hr.group_hr_user",
    )

    # --- helpers for downstream modules ---
    mcb_overtime_eligible = fields.Boolean(
        related="mcb_grade_id.overtime_eligible",
        store=True, readonly=True, groups="hr.group_hr_user",
    )
