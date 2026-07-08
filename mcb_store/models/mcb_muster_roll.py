from odoo import api, fields, models


class McbMusterRoll(models.Model):
    """STO-007 — NFI distribution muster roll linked to a project activity."""
    _name = "mcb.muster.roll"
    _description = "MCB NFI Distribution Muster Roll"
    _inherit = ["mail.thread", "mcb.fy.mixin"]

    name = fields.Char(default="New", copy=False, readonly=True)
    project_id = fields.Many2one("project.project", string="Project")
    task_id = fields.Many2one("project.task", string="Activity / Task",
                              domain="[('project_id', '=', project_id)]")
    product_id = fields.Many2one("product.product", string="Item (NFI)", required=True)
    date = fields.Date(default=fields.Date.context_today, required=True)
    location = fields.Char(string="Distribution Point (Camp/Union)")
    picking_id = fields.Many2one("stock.picking", string="Related Issue (SRF/Delivery)")
    line_ids = fields.One2many("mcb.muster.roll.line", "roll_id", string="Beneficiaries")
    total_qty = fields.Float(compute="_compute_total", store=True)
    state = fields.Selection([("draft", "Draft"), ("done", "Distributed")],
                             default="draft", tracking=True)

    @api.depends("line_ids.quantity")
    def _compute_total(self):
        for rec in self:
            rec.total_qty = sum(rec.line_ids.mapped("quantity"))

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = self._mcb_fy_sequence_next("mcb.muster.roll", "MRL")
        return super().create(vals_list)

    def action_done(self):
        self.write({"state": "done"})


class McbMusterRollLine(models.Model):
    _name = "mcb.muster.roll.line"
    _description = "Muster Roll Beneficiary Line"

    roll_id = fields.Many2one("mcb.muster.roll", required=True, ondelete="cascade")
    beneficiary_name = fields.Char(required=True)
    beneficiary_id_no = fields.Char(string="Beneficiary ID / NID / FCN")
    quantity = fields.Float(default=1)
    remarks = fields.Char()
