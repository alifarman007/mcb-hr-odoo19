from datetime import timedelta

from odoo import api, fields, models, _


class FleetVehicle(models.Model):
    _inherit = "fleet.vehicle"

    # VEH-002 register extras
    mcb_project_id = fields.Many2one("project.project", string="Assigned Project",
                                     tracking=True)
    mcb_vehicle_kind = fields.Selection([
        ("car", "Car"), ("motorbike", "Motorbike"), ("cng", "CNG / Auto"),
        ("other", "Other"),
    ], default="car", string="Vehicle Kind")
    mcb_insurance_expiry = fields.Date(string="Insurance Expiry", tracking=True)
    mcb_fitness_expiry = fields.Date(string="Fitness Certificate Expiry", tracking=True)
    mcb_log_ids = fields.One2many("mcb.vehicle.log", "vehicle_id", string="Log Book")

    # VEH-004 — 30-day expiry alerts
    @api.model
    def _cron_mcb_expiry_alert(self):
        horizon = fields.Date.context_today(self) + timedelta(days=30)
        for veh in self.search(["|", ("mcb_insurance_expiry", "<=", horizon),
                                ("mcb_fitness_expiry", "<=", horizon)]):
            user = veh.manager_id or self.env.ref("base.user_admin")
            expiring = []
            if veh.mcb_insurance_expiry and veh.mcb_insurance_expiry <= horizon:
                expiring.append(_("insurance (%s)", veh.mcb_insurance_expiry))
            if veh.mcb_fitness_expiry and veh.mcb_fitness_expiry <= horizon:
                expiring.append(_("fitness certificate (%s)", veh.mcb_fitness_expiry))
            if not expiring:
                continue
            already = self.env["mail.activity"].search_count([
                ("res_model", "=", "fleet.vehicle"), ("res_id", "=", veh.id),
                ("summary", "like", "VEH-004")], limit=1)
            if not already:
                self.env["mail.activity"].create({
                    "res_model_id": self.env["ir.model"]._get_id("fleet.vehicle"),
                    "res_id": veh.id,
                    "activity_type_id": self.env.ref("mail.mail_activity_data_todo").id,
                    "user_id": user.id,
                    "summary": _("VEH-004 — %s expiring within 30 days",
                                 " & ".join(expiring)),
                })
