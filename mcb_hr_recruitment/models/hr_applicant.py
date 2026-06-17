from odoo import api, fields, models


class HrApplicant(models.Model):
    _inherit = "hr.applicant"

    # REC-001 link
    mcb_requisition_id = fields.Many2one("mcb.hr.staff.requisition", string="Staff Requisition", index=True)

    # REC-005 candidate profile extras
    mcb_father_name = fields.Char(string="Father's Name", tracking=True)
    mcb_mother_name = fields.Char(string="Mother's Name", tracking=True)
    mcb_present_address = fields.Char(string="Present Address")
    mcb_permanent_address = fields.Char(string="Permanent Address")
    mcb_nid = fields.Char(string="NID / Birth Cert.")
    mcb_education_summary = fields.Text(string="Education Summary")
    mcb_experience_summary = fields.Text(string="Experience Summary")

    # REC-007 admit card
    mcb_admit_card_id = fields.Char(string="Admit Card ID", copy=False, readonly=True, index=True)
    mcb_admit_card_issued = fields.Boolean(string="Admit Card Issued", copy=False)
    mcb_exam_date = fields.Date(string="Exam Date")
    mcb_exam_time = fields.Char(string="Exam Time")
    mcb_exam_venue = fields.Char(string="Exam Venue")

    # REC-009 attendance
    mcb_attended_written = fields.Boolean(string="Attended Written")
    mcb_attended_oral = fields.Boolean(string="Attended Oral")

    # REC-010 / REC-011 marks
    # SRS v2 feedback: Written (50), Computer (20), Oral/VIVA (30).
    # Oral marking sheet now has only two per-examiner components:
    # Skills (15) + Knowledge (15) = 30.
    mcb_written_score = fields.Float(string="Written Score (50)")
    mcb_computer_score = fields.Float(string="Computer Score (20)")
    mcb_oral_score_skills = fields.Float(string="Oral — Skills (15)")
    mcb_oral_score_knowledge = fields.Float(string="Oral — Knowledge (15)")
    mcb_oral_score = fields.Float(
        string="Oral Total (30)", compute="_compute_oral_score", store=True,
    )
    mcb_total_score = fields.Float(
        string="Total Score", compute="_compute_total_score", store=True, aggregator="avg",
    )
    mcb_merit_rank = fields.Integer(string="Merit Rank", help="Auto-ranked by total score within the requisition.")

    # REC-012 selection flag
    mcb_selected = fields.Boolean(string="Selected (Merit list)", copy=False)

    @api.depends("mcb_oral_score_skills", "mcb_oral_score_knowledge")
    def _compute_oral_score(self):
        for rec in self:
            rec.mcb_oral_score = (
                (rec.mcb_oral_score_skills or 0)
                + (rec.mcb_oral_score_knowledge or 0)
            )

    @api.depends("mcb_written_score", "mcb_computer_score", "mcb_oral_score")
    def _compute_total_score(self):
        for rec in self:
            rec.mcb_total_score = (
                (rec.mcb_written_score or 0)
                + (rec.mcb_computer_score or 0)
                + (rec.mcb_oral_score or 0)
            )

    # REC-007 admit card generation
    def action_issue_admit_card(self):
        for rec in self:
            if not rec.mcb_admit_card_id:
                seq = self.env["ir.sequence"].next_by_code("mcb.hr.admit.card") or "00"
                proj = rec.mcb_requisition_id.project_code or "MCB"
                rec.mcb_admit_card_id = f"{proj}-O-{seq}"
            rec.mcb_admit_card_issued = True

    # REC-012 ranking
    def action_compute_merit_rank(self):
        requisitions = self.mapped("mcb_requisition_id")
        for req in requisitions:
            sorted_apps = req.applicant_ids.sorted(lambda r: r.mcb_total_score or 0, reverse=True)
            for i, app in enumerate(sorted_apps, start=1):
                app.mcb_merit_rank = i

    def action_mark_selected(self):
        self.write({"mcb_selected": True})

    # REC + ONB-001 — when applicant is hired (stage marked hired), create
    # an onboarding plan automatically. Hook into stage change.
    def write(self, vals):
        res = super().write(vals)
        if "stage_id" in vals:
            for rec in self:
                if rec.stage_id and rec.stage_id.hired_stage and rec.employee_id:
                    rec._mcb_post_hire()
        return res

    def _mcb_post_hire(self):
        # Hand off to mcb_hr_onboarding (if installed) to run its plan launcher.
        if hasattr(self.env["hr.employee"], "action_mcb_launch_onboarding"):
            self.employee_id.action_mcb_launch_onboarding()
