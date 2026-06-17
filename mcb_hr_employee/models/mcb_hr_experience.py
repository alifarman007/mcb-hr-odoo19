from odoo import fields, models


class McbHrExperience(models.Model):
    _name = "mcb.hr.experience"
    _description = "Employee Prior Work Experience"
    _order = "date_from desc"

    employee_id = fields.Many2one("hr.employee", required=True, ondelete="cascade")
    employer = fields.Char(required=True)
    position = fields.Char()
    date_from = fields.Date()
    date_to = fields.Date()
    responsibilities = fields.Text()
    reference_name = fields.Char()
    reference_phone = fields.Char()
