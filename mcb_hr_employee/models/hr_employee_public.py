from odoo import fields, models


class HrEmployeePublic(models.Model):
    """Mirror the non-sensitive MCB fields onto the public employee profile.

    `hr.employee.public` is the read-only model Odoo swaps in when a user without
    HR rights views employee data (e.g. an ordinary employee opening Expenses or
    Time Off). Any field we add to `hr.employee` and then show in a shared view
    must exist here too, otherwise those users get:

        "The fields ... are not available for employee public profiles."

    Only the staff ID is mirrored. Personal data - NID, parents' names, PF
    nominee, probation and service dates - deliberately stays on `hr.employee`
    so it remains visible to HR only.
    """
    _inherit = "hr.employee.public"

    mcb_employee_code = fields.Char(
        related="employee_id.mcb_employee_code", readonly=True,
        string="MCB Employee Code")
