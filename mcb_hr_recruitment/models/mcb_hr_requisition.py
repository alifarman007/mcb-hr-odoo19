from odoo import api, fields, models


class McbHrStaffRequisition(models.Model):
    _name = "mcb.hr.staff.requisition"
    _description = "MCB Staff Requisition (Form 21a/21b)"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "create_date desc"

    name = fields.Char(string="Requisition #", required=True, readonly=True, copy=False, default="New")
    state = fields.Selection([
        ("draft", "Draft"),
        ("pm_approval", "PM Approved"),
        ("hr_approval", "HR Approved"),
        ("ce_approval", "CE Approved"),
        ("published", "Published"),
        ("closed", "Closed"),
        ("cancelled", "Cancelled"),
    ], default="draft", tracking=True, required=True)

    request_date = fields.Date(default=fields.Date.context_today, tracking=True)
    requester_id = fields.Many2one("res.users", default=lambda s: s.env.user, tracking=True)
    department_id = fields.Many2one("hr.department", string="Department", required=True, tracking=True)

    # SRS REC-001 fields
    position_title = fields.Char(required=True, tracking=True)
    grade_id = fields.Many2one("mcb.hr.grade", string="Grade", tracking=True)
    number_of_vacancies = fields.Integer(default=1, required=True)
    gender_preference = fields.Selection([
        ("any", "Any"),
        ("male", "Male"),
        ("female", "Female"),
    ], default="any")
    employment_type = fields.Selection([
        ("permanent", "Permanent / Regular"),
        ("project", "Project / Contractual"),
        ("probationary", "Probationary"),
        ("support", "Support / Driver"),
    ], default="project", required=True)
    qualification = fields.Text(string="Minimum Qualifications")
    working_area = fields.Char(string="Working Area / Location")
    project_code = fields.Char(string="Project Code")
    donor = fields.Char(string="Donor")
    analytic_code = fields.Char(string="Analytic Cost Code")
    effective_date = fields.Date(string="Required From", tracking=True)
    proposed_salary = fields.Monetary(string="Proposed Salary", currency_field="currency_id")
    currency_id = fields.Many2one("res.currency", default=lambda s: s.env.company.currency_id)
    replacement = fields.Selection([
        ("new", "New Position"),
        ("replacement", "Replacement"),
    ], default="new", required=True)
    replacement_of = fields.Char(string="Replacement Of (Name)")
    justification = fields.Html()

    # SRS REC-003: budget check (light)
    budget_available = fields.Boolean(string="Budget Confirmed", tracking=True)
    budget_remarks = fields.Char()

    # REC-010 marks configuration carried at requisition level so each
    # recruitment can fine-tune the weights.
    # SRS v2 feedback: default Written 50, Computer 20, Oral/VIVA 30.
    marks_written = fields.Integer("Written marks (max)", default=50)
    marks_computer = fields.Integer("Computer marks (max)", default=20)
    marks_oral = fields.Integer("Oral / VIVA marks (max)", default=30)

    # Linked job / applicants
    job_id = fields.Many2one("hr.job", string="Linked Job Position", tracking=True)
    applicant_ids = fields.One2many("hr.applicant", "mcb_requisition_id", string="Applicants")
    applicant_count = fields.Integer(compute="_compute_applicant_count")

    expenditure_id = fields.Many2one("mcb.hr.recruitment.expenditure", string="Expenditure Top Sheet")

    @api.depends("applicant_ids")
    def _compute_applicant_count(self):
        for rec in self:
            rec.applicant_count = len(rec.applicant_ids)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = self.env["ir.sequence"].next_by_code("mcb.hr.staff.requisition") or "REQ/0000"
        return super().create(vals_list)

    def action_submit_pm(self):
        self.write({"state": "pm_approval"})

    def action_submit_hr(self):
        self.write({"state": "hr_approval"})

    def action_ce_approve(self):
        self.write({"state": "ce_approval"})

    def action_publish(self):
        for rec in self:
            if not rec.job_id:
                job = self.env["hr.job"].create({
                    "name": rec.position_title,
                    "department_id": rec.department_id.id,
                    "no_of_recruitment": rec.number_of_vacancies,
                    "description": rec.qualification or "",
                })
                rec.job_id = job.id
            rec.state = "published"

    def action_close(self):
        self.write({"state": "closed"})

    def action_cancel(self):
        self.write({"state": "cancelled"})

    def action_reset(self):
        self.write({"state": "draft"})

    def action_view_applicants(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": "Applicants",
            "res_model": "hr.applicant",
            "view_mode": "list,kanban,form",
            "domain": [("mcb_requisition_id", "=", self.id)],
        }
