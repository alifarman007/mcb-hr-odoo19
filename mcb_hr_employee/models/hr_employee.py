from odoo import api, fields, models


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    # --- EMP-001 personal extras ---
    mcb_nid = fields.Char(
        string="National ID (NID)",
        groups="hr.group_hr_user",
        tracking=True,
        help="Bangladesh National Identification Number — required for payroll & PF.",
    )
    mcb_father_name = fields.Char(string="Father's Name", groups="hr.group_hr_user", tracking=True)
    mcb_mother_name = fields.Char(string="Mother's Name", groups="hr.group_hr_user", tracking=True)
    mcb_blood_group = fields.Selection([
        ("A+", "A+"), ("A-", "A-"),
        ("B+", "B+"), ("B-", "B-"),
        ("AB+", "AB+"), ("AB-", "AB-"),
        ("O+", "O+"), ("O-", "O-"),
    ], string="Blood Group", groups="hr.group_hr_user")
    mcb_emergency_relation = fields.Char(string="Emergency Contact Relation", groups="hr.group_hr_user")
    mcb_education_ids = fields.One2many("mcb.hr.education", "employee_id", string="Education")
    mcb_experience_ids = fields.One2many("mcb.hr.experience", "employee_id", string="Prior Experience")

    # --- EMP-005 service dates ---
    mcb_service_continuity_date = fields.Date(
        string="Service Continuity Date",
        groups="hr.group_hr_user",
        tracking=True,
        help="Earliest joining date used for gratuity / PF tenure calculations.",
    )
    mcb_probation_start_date = fields.Date(string="Probation Start", groups="hr.group_hr_user", tracking=True)
    mcb_probation_end_date = fields.Date(string="Probation End", groups="hr.group_hr_user", tracking=True)
    mcb_confirmation_date = fields.Date(string="Confirmation Date", groups="hr.group_hr_user", tracking=True)

    # --- EMP-006 PF nominee ---
    mcb_pf_nominee_name = fields.Char(string="PF Nominee Name", groups="hr.group_hr_user")
    mcb_pf_nominee_relation = fields.Char(string="PF Nominee Relation", groups="hr.group_hr_user")
    mcb_pf_nominee_nid = fields.Char(string="PF Nominee NID", groups="hr.group_hr_user")
    mcb_pf_nominee_share = fields.Float(string="PF Nominee Share (%)", default=100.0, groups="hr.group_hr_user")

    # --- EMP-008 MCB employee code (project-prefixed) ---
    mcb_employee_code = fields.Char(
        string="MCB Employee Code",
        copy=False,
        readonly=True,
        index=True,
        help="Auto-generated project-prefixed staff code, e.g. MEAL-O-01.",
    )

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        for rec in records:
            if not rec.mcb_employee_code:
                rec.mcb_employee_code = rec._mcb_generate_employee_code()
        return records

    def _mcb_generate_employee_code(self):
        self.ensure_one()
        version = self.current_version_id or self.version_id
        prefix = "MCB"
        if version and version.mcb_project_code:
            prefix = version.mcb_project_code
        seq = self.env["ir.sequence"].next_by_code("mcb.hr.employee.code") or "00"
        return f"{prefix}-{seq}"
