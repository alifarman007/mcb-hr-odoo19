from odoo import api, fields, models, _
from odoo.exceptions import UserError


class AccountAsset(models.Model):
    _inherit = "account.asset"

    # AST-001/003 register columns
    mcb_asset_code = fields.Char(string="Asset ID Number", copy=False, readonly=True,
                                 index=True)
    mcb_location = fields.Char(string="Location")
    mcb_condition = fields.Selection([
        ("good", "Good"), ("fair", "Fair"),
        ("repairable", "Repairable"), ("damaged", "Damaged"),
    ], default="good", string="Condition", tracking=True)
    mcb_custodian_id = fields.Many2one("hr.employee", string="Name of User / Custodian",
                                       tracking=True)
    mcb_project_analytic_id = fields.Many2one(
        "account.analytic.account", string="Project / Donor", tracking=True,
        help="AST-003 — funding source for donor reporting.")
    mcb_funded_by = fields.Char(string="Funded By")
    mcb_ce_disposal_approved = fields.Boolean(
        string="CE Disposal Approval", tracking=True, copy=False,
        help="AST-005 — disposal/write-off requires prior CE approval.")
    mcb_transfer_ids = fields.One2many("mcb.asset.transfer", "asset_id",
                                       string="Transfer History")

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        for rec in records:
            if not rec.mcb_asset_code:
                rec.mcb_asset_code = self.env["ir.sequence"].next_by_code(
                    "mcb.asset.code") or "AST/000"
        return records

    def action_mcb_ce_approve_disposal(self):
        if not self.env.user.has_group("mcb_hr_employee.group_mcb_ce"):
            raise UserError(_("AST-005 — only the Chief Executive group may approve disposal."))
        self.write({"mcb_ce_disposal_approved": True})

    def set_to_close(self, invoice_line_ids, date=None, message=None):
        for asset in self:
            if not asset.mcb_ce_disposal_approved:
                raise UserError(_(
                    "AST-005 — asset '%s' cannot be disposed/sold without CE approval. "
                    "Use the 'CE Approve Disposal' button first.", asset.name))
        return super().set_to_close(invoice_line_ids, date=date, message=message)

    def _mcb_depreciation_figures(self, date_from, date_to):
        """Annexure-07 columns: opening / charge in period / adjustment / closing."""
        self.ensure_one()
        posted = self.depreciation_move_ids.filtered(lambda m: m.state == "posted")
        opening = sum(m.depreciation_value for m in posted if m.date < date_from)
        charge = sum(m.depreciation_value for m in posted
                     if date_from <= m.date <= date_to)
        closing = opening + charge
        wdv = self.original_value - closing
        return {"opening": opening, "charge": charge, "adjustment": 0.0,
                "closing": closing, "wdv": wdv}


class McbAssetTransfer(models.Model):
    """AST-006 — asset transfer between projects/locations/users."""
    _name = "mcb.asset.transfer"
    _description = "MCB Asset Transfer"
    _order = "date desc"

    asset_id = fields.Many2one("account.asset", required=True, ondelete="cascade")
    date = fields.Date(default=fields.Date.context_today, required=True)
    from_project_id = fields.Many2one("account.analytic.account", string="From Project")
    to_project_id = fields.Many2one("account.analytic.account", string="To Project")
    from_location = fields.Char()
    to_location = fields.Char()
    from_custodian_id = fields.Many2one("hr.employee", string="From User")
    to_custodian_id = fields.Many2one("hr.employee", string="To User")
    note = fields.Char()

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        for rec in records:
            rec.asset_id.write({
                "mcb_project_analytic_id": rec.to_project_id.id or rec.asset_id.mcb_project_analytic_id.id,
                "mcb_location": rec.to_location or rec.asset_id.mcb_location,
                "mcb_custodian_id": rec.to_custodian_id.id or rec.asset_id.mcb_custodian_id.id,
            })
            rec.asset_id.message_post(body=_(
                "Asset transferred: %s → %s / %s → %s (%s)",
                rec.from_project_id.name or "-", rec.to_project_id.name or "-",
                rec.from_location or "-", rec.to_location or "-", rec.date))
        return records
