from odoo import api, fields, models
from odoo.exceptions import UserError


class HrExpense(models.Model):
    _inherit = "hr.expense"

    # EXP-001 trigger conditions
    mcb_grade_id = fields.Many2one(
        "mcb.hr.grade", string="Grade",
        compute="_compute_mcb_grade", store=True, readonly=False,
    )
    mcb_grade_band = fields.Selection(
        related="mcb_grade_id.band", string="Grade Band", store=True, readonly=True,
    )
    mcb_is_taDa = fields.Boolean(
        string="TA / DA Claim",
        help="Flag for travel-allowance / daily-allowance claims (EXP-001).",
    )
    mcb_distance_km = fields.Float(
        string="Distance Travelled (km)",
        help="EXP-001 — 50 km+ or overnight stay triggers per-diem auto-fill.",
    )
    mcb_overnight_stay = fields.Boolean(string="Overnight Stay")
    mcb_air_travel = fields.Boolean(string="Air Travel (Economy only)")
    mcb_air_class = fields.Selection([
        ("economy", "Economy"),
        ("business", "Business"),
        ("first", "First"),
    ], string="Air Class", default="economy",
        help="EXP-003 — only Economy allowed; system rejects other classes.")
    mcb_field_visit_hours = fields.Float(
        string="Field-Visit Duration (hours)",
        help="EXP-007 — 6-hour field-visit rule triggers BDT 400 lunch.",
    )

    # EXP-006 donor analytic
    mcb_analytic_code = fields.Char(string="Analytic Cost Code")
    mcb_donor = fields.Char(string="Donor")
    mcb_project_code = fields.Char(string="Project Code")

    @api.depends("employee_id")
    def _compute_mcb_grade(self):
        for exp in self:
            exp.mcb_grade_id = exp.employee_id.mcb_grade_id

    def action_apply_per_diem(self):
        """EXP-001 auto-populate per-diem amount based on grade band."""
        for exp in self:
            if not exp.mcb_grade_band:
                raise UserError("Employee has no MCB grade assigned.")
            per_diem = self.env["mcb.hr.per.diem"].for_grade_band(exp.mcb_grade_band)
            if not per_diem:
                raise UserError(f"No per-diem row configured for band {exp.mcb_grade_band}.")
            amount = per_diem.full_day if (exp.mcb_distance_km >= 50 or exp.mcb_overnight_stay) else per_diem.field_visit_lunch
            exp.total_amount_currency = amount
        return True

    @api.constrains("mcb_air_travel", "mcb_air_class")
    def _check_air_class(self):
        for exp in self:
            if exp.mcb_air_travel and exp.mcb_air_class in ("business", "first"):
                raise UserError(
                    "EXP-003 — Air travel for MCB is restricted to Economy class only."
                )

    # EXP-002 — auto-route to CE when air travel or Grade 1-2 employee
    mcb_requires_ce_approval = fields.Boolean(
        string="Requires CE Approval",
        compute="_compute_requires_ce_approval", store=True,
        help="EXP-002: CE approval is required for air travel or Grade 1–2 (senior) staff travel.",
    )
    mcb_ce_approved_by = fields.Many2one("res.users", string="CE Approved By",
        readonly=True, copy=False, tracking=True)
    mcb_ce_approved_on = fields.Datetime(string="CE Approved On",
        readonly=True, copy=False)

    @api.depends("mcb_air_travel", "mcb_grade_id", "mcb_is_taDa")
    def _compute_requires_ce_approval(self):
        for exp in self:
            grade_code = exp.mcb_grade_id.code or ""
            senior_grade = grade_code in ("G1", "G2")
            exp.mcb_requires_ce_approval = bool(
                exp.mcb_is_taDa and (exp.mcb_air_travel or senior_grade)
            )

    def action_mcb_ce_approve(self):
        """EXP-002 — Explicit CE approval step. Only members of the CE group may click."""
        ce_group = self.env.ref("mcb_hr_employee.group_mcb_ce", raise_if_not_found=False)
        if ce_group and not self.env.user.has_group("mcb_hr_employee.group_mcb_ce"):
            raise UserError(
                "EXP-002 — Only members of the MCB Chief Executive (CE) group "
                "can give this approval. Please ask the CE to log in and approve."
            )
        for exp in self:
            exp.mcb_ce_approved_by = self.env.user
            exp.mcb_ce_approved_on = fields.Datetime.now()
            exp.message_post(
                body=f"<strong>CE approval granted</strong> by {self.env.user.name} "
                     f"(EXP-002 — air travel / senior-grade expense)."
            )
        return True

    @api.constrains("state", "mcb_requires_ce_approval", "mcb_ce_approved_by")
    def _check_ce_approval(self):
        # Block posting/approval if CE approval is still pending
        for exp in self:
            if (
                exp.mcb_requires_ce_approval
                and not exp.mcb_ce_approved_by
                and exp.state in ("approved", "done", "posted")
            ):
                raise UserError(
                    "EXP-002 — This claim requires CE approval before posting. "
                    "Click 'CE Approve' (a member of the CE group must be logged in)."
                )
