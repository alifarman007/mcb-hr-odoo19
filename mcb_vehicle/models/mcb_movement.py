from odoo import api, fields, models


class McbMovementRegister(models.Model):
    """Annexure-09 — Daily Movement Register (MOV-001..004)."""
    _name = "mcb.movement.register"
    _description = "MCB Daily Movement Register (Annexure-09)"
    _order = "departure_date desc, id desc"

    name = fields.Char(default="New", copy=False, readonly=True)
    employee_id = fields.Many2one("hr.employee", required=True)
    designation = fields.Char(related="employee_id.job_title")
    office_location = fields.Char(string="Project Office / Location (MOV-002)")
    destination = fields.Char(required=True)
    purpose = fields.Char(required=True)
    departure_date = fields.Date(required=True, default=fields.Date.context_today)
    departure_time = fields.Float()
    arrival_date = fields.Date()
    arrival_time = fields.Float()
    travel_auth_id = fields.Many2one(
        "mcb.travel.authorization",
        string="Travel Authorization (MOV-004)",
        domain="[('employee_id', '=', employee_id)]")
    expense_id = fields.Many2one(
        "hr.expense", string="Travel Bill / Expense (MOV-003)",
        domain="[('employee_id', '=', employee_id)]")
    remarks = fields.Char()

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = self.env["ir.sequence"].next_by_code(
                    "mcb.movement.register") or "MOV/000"
        return super().create(vals_list)
