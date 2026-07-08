from odoo import api, fields, models


class McbPaymentChecklist(models.Model):
    """Annexure-28 — Checklist for Payment Voucher (VOU-007, TAX-003)."""
    _name = "mcb.payment.checklist"
    _description = "MCB Payment Voucher Checklist (Annexure-28)"
    _inherit = ["mail.thread"]

    name = fields.Char(default="New", copy=False, readonly=True)
    move_id = fields.Many2one(
        "account.move", string="Payment Voucher / Bill", required=True,
        domain="[('move_type', 'in', ('in_invoice', 'entry'))]",
    )
    company_id = fields.Many2one(related="move_id.company_id", store=True)
    project_name = fields.Char(string="Name of Project / Office")
    funded_by = fields.Char()
    prepared_by_id = fields.Many2one("res.users", default=lambda s: s.env.user, readonly=True)
    checked_by_id = fields.Many2one("res.users", tracking=True)
    line_ids = fields.One2many("mcb.payment.checklist.line", "checklist_id", string="Items")
    state = fields.Selection([
        ("draft", "Draft"),
        ("done", "Verified"),
    ], default="draft", tracking=True)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = self.env["ir.sequence"].next_by_code("mcb.payment.checklist") or "PVC/000"
        records = super().create(vals_list)
        template_items = self.env["mcb.checklist.item.template"].search(
            [("checklist_type", "=", "payment")], order="sequence"
        )
        for rec in records:
            if not rec.line_ids and template_items:
                rec.line_ids = [(0, 0, {"name": t.name, "sequence": t.sequence})
                                for t in template_items]
        return records

    def action_done(self):
        self.write({"state": "done", "checked_by_id": self.env.user.id})


class McbPaymentChecklistLine(models.Model):
    _name = "mcb.payment.checklist.line"
    _description = "Payment Checklist Line"
    _order = "sequence, id"

    checklist_id = fields.Many2one("mcb.payment.checklist", required=True, ondelete="cascade")
    sequence = fields.Integer(default=10)
    name = fields.Char(string="Particulars", required=True)
    status = fields.Selection([
        ("yes", "Yes"), ("no", "No"), ("na", "N/A"),
    ], default="na")
    remarks = fields.Char()


class McbChecklistItemTemplate(models.Model):
    """Seedable checklist items (Annexure-28 payment / Annexure-29 procurement)."""
    _name = "mcb.checklist.item.template"
    _description = "MCB Checklist Item Template"
    _order = "checklist_type, sequence"

    name = fields.Char(required=True)
    sequence = fields.Integer(default=10)
    checklist_type = fields.Selection([
        ("payment", "Payment Voucher (Annexure-28)"),
        ("procurement", "Procurement Procedures (Annexure-29)"),
    ], required=True, default="payment")
