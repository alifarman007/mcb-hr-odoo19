from odoo import api, fields, models


class McbMealIndicator(models.Model):
    """MON-007 (Should Have) — MEAL indicator scaffold linked to project activities."""
    _name = "mcb.meal.indicator"
    _description = "MCB MEAL Indicator"

    name = fields.Char(required=True)
    project_id = fields.Many2one("project.project", required=True)
    task_id = fields.Many2one("project.task", string="Linked Activity",
                              domain="[('project_id', '=', project_id)]")
    unit = fields.Char(default="count")
    target = fields.Float()
    achieved = fields.Float()
    achievement_pct = fields.Float(compute="_compute_pct", store=True)
    period = fields.Char(string="Reporting Period (e.g. Q1 25-26)")
    note = fields.Char()

    @api.depends("target", "achieved")
    def _compute_pct(self):
        for rec in self:
            rec.achievement_pct = (rec.achieved / rec.target * 100.0) if rec.target else 0.0
