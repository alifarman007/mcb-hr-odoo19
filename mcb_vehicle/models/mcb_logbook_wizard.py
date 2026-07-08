from dateutil.relativedelta import relativedelta

from odoo import fields, models


class McbLogbookWizard(models.TransientModel):
    """Annexure-10 monthly log book PDF + VEH-003 usage summary + Annexure-25
    travel bill (movement-linked expenses)."""
    _name = "mcb.logbook.wizard"
    _inherit = ["mcb.xlsx.mixin"]
    _description = "Monthly Vehicle Log Book (Annexure-10)"

    vehicle_id = fields.Many2one("fleet.vehicle", required=True)
    month_date = fields.Date(
        required=True, default=lambda s: fields.Date.context_today(s).replace(day=1))

    def _period(self):
        start = self.month_date.replace(day=1)
        return start, start + relativedelta(months=1, days=-1)

    def _logs(self):
        start, end = self._period()
        return self.env["mcb.vehicle.log"].search([
            ("vehicle_id", "=", self.vehicle_id.id),
            ("date", ">=", start), ("date", "<=", end)], order="date")

    def action_print_pdf(self):
        return self.env.ref("mcb_vehicle.action_report_mcb_logbook").report_action(self)

    def action_export_xlsx(self):
        rows = [[str(l.date), l.employee_id.name or l.driver_name or "", l.purpose,
                 l.location_from or "", l.location_to or "", l.total_time,
                 l.meter_start, l.meter_end, l.km_run, l.fuel_litre, l.fuel_cost,
                 l.remarks or ""] for l in self._logs()]
        return self._mcb_xlsx_download(
            f"logbook_{self.vehicle_id.license_plate or self.vehicle_id.id}_{self.month_date:%Y_%m}.xlsx",
            "Vehicle Log Book",
            ["Date", "User", "Purpose", "From", "To", "Total Time", "Meter Start",
             "Meter End", "KM Run", "Fuel (L)", "Fuel Cost", "Remarks"],
            rows)
