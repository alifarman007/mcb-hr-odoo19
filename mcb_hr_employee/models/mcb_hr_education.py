from odoo import fields, models


class McbHrEducation(models.Model):
    _name = "mcb.hr.education"
    _description = "Employee Education Record"
    _order = "passing_year desc"

    employee_id = fields.Many2one("hr.employee", required=True, ondelete="cascade")
    degree = fields.Char(string="Degree / Qualification", required=True)
    institution = fields.Char(string="Institution / Board")
    major = fields.Char(string="Major / Subject")
    passing_year = fields.Integer(string="Passing Year")
    result = fields.Char(string="Result / Grade")
    document = fields.Binary(string="Certificate (PDF)")
    document_filename = fields.Char()
