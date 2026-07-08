from odoo import fields, models


class McbStoreRegisterWizard(models.TransientModel):
    """Annexure-08 Store Register (per item, running balance) and the Monthly Stock
    Report (opening/receipts/issues/closing per item) over native stock.move data
    (STO-001/002)."""
    _name = "mcb.store.register.wizard"
    _inherit = ["mcb.xlsx.mixin"]
    _description = "Store Register / Monthly Stock Report (Annexure-08)"

    location_id = fields.Many2one(
        "stock.location", required=True, domain="[('usage', '=', 'internal')]",
        default=lambda s: s.env.ref("stock.stock_location_stock", raise_if_not_found=False))
    product_id = fields.Many2one("product.product", string="Item (for the register)")
    date_from = fields.Date(required=True)
    date_to = fields.Date(required=True, default=fields.Date.context_today)
    project_name = fields.Char(string="Name of Project / Office")
    funded_by = fields.Char()

    def _moves(self, product):
        return self.env["stock.move"].search([
            ("state", "=", "done"),
            ("product_id", "=", product.id),
            "|", ("location_id", "=", self.location_id.id),
                 ("location_dest_id", "=", self.location_id.id),
            ("date", ">=", fields.Datetime.to_datetime(self.date_from)),
            ("date", "<=", fields.Datetime.to_datetime(self.date_to).replace(
                hour=23, minute=59, second=59)),
        ], order="date, id")

    def _opening_qty(self, product):
        grouped_in = self.env["stock.move"]._read_group(
            [("state", "=", "done"), ("product_id", "=", product.id),
             ("location_dest_id", "=", self.location_id.id),
             ("date", "<", fields.Datetime.to_datetime(self.date_from))],
            [], ["product_qty:sum"])
        grouped_out = self.env["stock.move"]._read_group(
            [("state", "=", "done"), ("product_id", "=", product.id),
             ("location_id", "=", self.location_id.id),
             ("date", "<", fields.Datetime.to_datetime(self.date_from))],
            [], ["product_qty:sum"])
        return (grouped_in[0][0] or 0.0) - (grouped_out[0][0] or 0.0)

    def _register_rows(self):
        """Annexure-08 — running balance for one product."""
        product = self.product_id
        rows, balance = [], self._opening_qty(product)
        opening = balance
        for m in self._moves(product):
            received = m.product_qty if m.location_dest_id == self.location_id else 0.0
            issued = m.product_qty if m.location_id == self.location_id else 0.0
            balance += received - issued
            rows.append({
                "date": m.date.date(),
                "grn": m.picking_id.name if received else "",
                "received": received,
                "rate": m.purchase_line_id.price_unit if m.purchase_line_id else 0.0,
                "srf": m.picking_id.origin or m.picking_id.name if issued else "",
                "issued": issued,
                "balance": balance,
                "recipient": m.picking_id.partner_id.name or "",
            })
        return opening, rows

    def _monthly_rows(self):
        """STO-002 — per-product opening / receipts / issues / closing."""
        products = self.env["stock.move"].search([
            ("state", "=", "done"),
            "|", ("location_id", "=", self.location_id.id),
                 ("location_dest_id", "=", self.location_id.id),
        ]).mapped("product_id")
        rows = []
        for p in products:
            opening = self._opening_qty(p)
            received = issued = 0.0
            for m in self._moves(p):
                if m.location_dest_id == self.location_id:
                    received += m.product_qty
                else:
                    issued += m.product_qty
            rows.append({"product": p, "opening": opening, "received": received,
                         "issued": issued, "closing": opening + received - issued})
        return rows

    def action_print_register(self):
        return self.env.ref("mcb_store.action_report_mcb_store_register").report_action(self)

    def action_print_monthly(self):
        return self.env.ref("mcb_store.action_report_mcb_monthly_stock").report_action(self)

    def action_export_xlsx(self):
        rows = [[r["product"].display_name, r["opening"], r["received"],
                 r["issued"], r["closing"]] for r in self._monthly_rows()]
        return self._mcb_xlsx_download(
            f"monthly_stock_{self.date_to}.xlsx", "Monthly Stock Report",
            ["Item", "Opening", "Receipts", "Issues", "Closing"],
            rows)
