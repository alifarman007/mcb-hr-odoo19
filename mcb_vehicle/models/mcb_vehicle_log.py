from odoo import api, fields, models


class McbVehicleLog(models.Model):
    """Annexure-10 — Vehicle/MC Log Book daily trip line (VEH-001).
    Saving a line syncs the fleet odometer (end reading)."""
    _name = "mcb.vehicle.log"
    _description = "MCB Vehicle Log Book Line (Annexure-10)"
    _order = "date desc, id desc"

    vehicle_id = fields.Many2one("fleet.vehicle", required=True, index=True)
    date = fields.Date(required=True, default=fields.Date.context_today)
    employee_id = fields.Many2one("hr.employee", string="Name & Designation (User)")
    driver_name = fields.Char(string="Driver")
    purpose = fields.Char(required=True)
    location_from = fields.Char(string="From")
    location_to = fields.Char(string="To")
    time_start = fields.Float(string="Time Start")
    time_end = fields.Float(string="Time End")
    total_time = fields.Float(compute="_compute_totals", store=True)
    meter_start = fields.Float(string="Meter Start (km)")
    meter_end = fields.Float(string="Meter End (km)")
    km_run = fields.Float(compute="_compute_totals", store=True, string="KM Run")
    fuel_litre = fields.Float(string="Fuel (Litre)")
    fuel_cost = fields.Monetary(currency_field="currency_id", string="Fuel Cost")
    lub = fields.Float(string="Lubricant")
    project_id = fields.Many2one(
        "project.project", string="Project",
        compute="_compute_project", store=True, readonly=False)
    remarks = fields.Char()
    currency_id = fields.Many2one("res.currency", default=lambda s: s.env.company.currency_id)

    @api.depends("time_start", "time_end", "meter_start", "meter_end")
    def _compute_totals(self):
        for rec in self:
            rec.total_time = max((rec.time_end or 0) - (rec.time_start or 0), 0.0)
            rec.km_run = max((rec.meter_end or 0) - (rec.meter_start or 0), 0.0)

    @api.depends("vehicle_id")
    def _compute_project(self):
        for rec in self:
            if not rec.project_id:
                rec.project_id = rec.vehicle_id.mcb_project_id

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        for rec in records:
            if rec.meter_end:
                self.env["fleet.vehicle.odometer"].create({
                    "vehicle_id": rec.vehicle_id.id,
                    "value": rec.meter_end,
                    "date": rec.date,
                })
        return records
