from odoo import api, fields, models


class McbHrPerDiem(models.Model):
    """SRS table 14 — per-diem rates per grade band.

    Used to auto-populate expense line amounts when an employee submits a
    TA/DA claim (EXP-001). Editable by HR.
    """
    _name = "mcb.hr.per.diem"
    _description = "MCB Per Diem Rate Table"
    _order = "sequence"

    name = fields.Char(compute="_compute_name", store=True)
    sequence = fields.Integer(default=10)
    band = fields.Selection([
        ("senior", "Senior (Grade 1–5)"),
        ("mid", "Mid-level (Grade 6–8)"),
        ("support", "Support / Driver (Grade 9–10)"),
    ], required=True)
    breakfast = fields.Monetary(currency_field="currency_id")
    lunch = fields.Monetary(currency_field="currency_id")
    afternoon = fields.Monetary(currency_field="currency_id")
    dinner = fields.Monetary(currency_field="currency_id")
    full_day = fields.Monetary(currency_field="currency_id")
    field_visit_lunch = fields.Monetary(
        string="Field-Visit Lunch", currency_field="currency_id",
        help="EXP-007 — 6-hour field-visit lunch (if office does not provide food).",
        default=400.0,
    )
    rc_ta = fields.Monetary(
        string="RC Member TA", currency_field="currency_id",
        help="REC-015 — Recruitment Committee Member TA (default BDT 2,000).",
        default=2000.0,
    )
    staff_ta = fields.Monetary(
        string="Staff TA", currency_field="currency_id",
        help="REC-015 — Staff TA (default BDT 1,000).",
        default=1000.0,
    )
    support_ta = fields.Monetary(
        string="Support TA", currency_field="currency_id",
        help="REC-015 — Support / Driver TA (default BDT 300).",
        default=300.0,
    )
    currency_id = fields.Many2one(
        "res.currency", default=lambda s: s.env.ref("base.BDT", raise_if_not_found=False) or s.env.company.currency_id,
    )

    _band_unique = models.Constraint(
        "unique(band)",
        "Only one per-diem row may exist per band.",
    )

    @api.depends("band", "full_day")
    def _compute_name(self):
        for rec in self:
            band_label = dict(self._fields["band"].selection).get(rec.band, "")
            rec.name = f"{band_label} — full day {rec.full_day}"

    @api.model
    def for_grade_band(self, band):
        return self.search([("band", "=", band)], limit=1)
