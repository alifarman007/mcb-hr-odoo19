from odoo import api, fields, models
from odoo.exceptions import UserError


REVISION_TYPES = [
    ("promotion", "Promotion"),
    ("transfer", "Transfer"),
    ("revision", "Salary Revision"),
    ("reappointment", "Re-appointment"),
    ("extension", "Service Extension"),
]


class McbHrSalaryRevisionWizard(models.TransientModel):
    """PAY-002 — Trigger a new hr.version when an employee is promoted /
    transferred / has salary revised / is re-appointed. Produces a printable
    letter on the new version and writes a chatter entry on the employee.
    """
    _name = "mcb.hr.salary.revision.wizard"
    _description = "MCB Salary Revision / Promotion Wizard"

    employee_id = fields.Many2one("hr.employee", required=True,
        default=lambda s: s.env.context.get("active_id")
            if s.env.context.get("active_model") == "hr.employee" else False)
    revision_type = fields.Selection(REVISION_TYPES, required=True, default="revision")
    effective_date = fields.Date(required=True, default=fields.Date.context_today)

    current_grade_id = fields.Many2one("mcb.hr.grade", related="employee_id.mcb_grade_id", readonly=True)
    current_wage = fields.Monetary(related="employee_id.wage", readonly=True, currency_field="currency_id")
    current_job_id = fields.Many2one("hr.job", related="employee_id.job_id", readonly=True)
    current_department_id = fields.Many2one("hr.department", related="employee_id.department_id", readonly=True)
    current_project_code = fields.Char(related="employee_id.mcb_project_code", readonly=True)
    current_working_area = fields.Char(string="Current Working Area",
        compute="_compute_current_area", readonly=True)

    new_grade_id = fields.Many2one("mcb.hr.grade", string="New Grade")
    new_wage = fields.Monetary(string="New Monthly Salary (BDT)", currency_field="currency_id")
    new_job_id = fields.Many2one("hr.job", string="New Job Position")
    new_department_id = fields.Many2one("hr.department", string="New Department")
    new_project_code = fields.Char(string="New Project Code")
    new_working_area = fields.Char(string="New Working Area")
    new_contract_end_date = fields.Date(string="New Contract End",
        help="For extensions / re-appointments.")
    reason = fields.Html(string="Reason / Justification")

    currency_id = fields.Many2one("res.currency",
        default=lambda s: s.env.company.currency_id)

    @api.depends("employee_id")
    def _compute_current_area(self):
        for wiz in self:
            wiz.current_working_area = (
                wiz.employee_id.work_location_id.name
                or wiz.employee_id.address_id.city or ""
            )

    @api.onchange("revision_type", "employee_id")
    def _onchange_defaults(self):
        if not self.employee_id:
            return
        if self.revision_type in ("revision", "extension") and not self.new_grade_id:
            self.new_grade_id = self.employee_id.mcb_grade_id
        if self.revision_type == "extension" and not self.new_wage:
            self.new_wage = self.employee_id.wage

    def action_apply(self):
        self.ensure_one()
        if not self.new_wage and self.revision_type != "transfer":
            raise UserError("Please enter the new monthly salary.")

        version_vals = {
            "employee_id": self.employee_id.id,
            "date_version": self.effective_date,
            "wage": self.new_wage or self.employee_id.wage,
            "mcb_grade_id": (self.new_grade_id or self.employee_id.mcb_grade_id).id,
            "mcb_project_code": self.new_project_code or self.employee_id.mcb_project_code,
            "department_id": (self.new_department_id or self.employee_id.department_id).id,
            "job_id": (self.new_job_id or self.employee_id.job_id).id,
            "name": dict(REVISION_TYPES).get(self.revision_type),
        }
        if self.new_contract_end_date:
            version_vals["contract_date_end"] = self.new_contract_end_date

        new_version = self.env["hr.version"].create(version_vals)

        # Make the new version current
        self.employee_id.write({"version_id": new_version.id})

        # Audit message
        self.employee_id.message_post(
            body=(
                f"<strong>Salary revision applied</strong> "
                f"({dict(REVISION_TYPES).get(self.revision_type)}) "
                f"effective {self.effective_date}<br/>"
                f"New wage: BDT {self.new_wage or self.employee_id.wage}<br/>"
                f"Reason: {self.reason or '(no reason supplied)'}"
            ),
            subject="MCB Salary Revision",
        )

        # Print the letter
        report_xmlid = {
            "promotion": "mcb_hr_payroll.action_report_mcb_salary_revision_letter",
            "revision": "mcb_hr_payroll.action_report_mcb_salary_revision_letter",
            "transfer": "mcb_hr_payroll.action_report_mcb_transfer_letter",
            "reappointment": "mcb_hr_payroll.action_report_mcb_reappointment_letter",
            "extension": "mcb_hr_payroll.action_report_mcb_service_extension_letter",
        }.get(self.revision_type, "mcb_hr_payroll.action_report_mcb_salary_revision_letter")
        return self.env.ref(report_xmlid).report_action(self)
