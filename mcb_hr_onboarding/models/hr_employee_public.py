from odoo import fields, models


class HrEmployeePublic(models.Model):
    """Onboarding status on the public employee profile.

    Needed for the same reason as in mcb_hr_employee: without these, an ordinary
    employee (no HR rights) hits an Access Error whenever a shared view asks for
    them. Neither field is personal data - they only say whether the standard
    orientation plan has been started.
    """
    _inherit = "hr.employee.public"

    mcb_onboarding_plan_id = fields.Many2one(
        related="employee_id.mcb_onboarding_plan_id", readonly=True,
        string="Onboarding Plan")
    mcb_onboarding_launched = fields.Boolean(
        related="employee_id.mcb_onboarding_launched", readonly=True,
        string="Onboarding Launched")
    mcb_onboarding_progress = fields.Float(
        related="employee_id.mcb_onboarding_progress", readonly=True,
        string="Onboarding Progress")
