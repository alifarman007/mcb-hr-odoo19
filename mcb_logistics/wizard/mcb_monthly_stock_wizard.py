from odoo import api, fields, models, _
from odoo.exceptions import UserError


class McbMonthlyStockWizard(models.TransientModel):
    """LOG-008 — Monthly Stock Report.

    SOP: 'The Stock Report is used to report the inventory position/holding for all
    inventory items by Purchase Order PO, at warehouse level... normally monthly.'
    The client's Monthly Stock Report Form carries seventeen columns, keyed on
    'Waybill Number or PO Number' — so the report is per item per consignment, not
    merely per item.
    """
    _name = "mcb.monthly.stock.wizard"
    _description = "MCB Monthly Stock Report"
    _inherit = ["mcb.xlsx.mixin"]

    month_date = fields.Date(string="Month", required=True,
                             default=lambda s: fields.Date.context_today(s).replace(day=1))
    warehouse_id = fields.Many2one("stock.warehouse", required=True)
    project_id = fields.Many2one("project.project", string="Project / Office")
    donor = fields.Char(string="Funded By")

    def _period(self):
        self.ensure_one()
        start = self.month_date.replace(day=1)
        end = (start + fields.date_utils.get_timedelta(1, "month"))
        return start, end

    def _collect(self):
        """One row per bin/stack card — i.e. per item per PO consignment."""
        self.ensure_one()
        start, end = self._period()
        cards = self.env["mcb.bin.card"].search([
            ("warehouse_id", "=", self.warehouse_id.id)])
        rows = []
        for card in cards:
            before = card.line_ids.filtered(lambda l: l.date and l.date < start)
            during = card.line_ids.filtered(lambda l: l.date and start <= l.date < end)
            opening = card.opening_balance + sum(before.mapped("qty_in")) \
                - sum(before.mapped("qty_out"))
            received = sum(during.mapped("qty_in"))
            issued = sum(during.mapped("qty_out"))
            # a disposal is written on the card as an issue referencing a DSP document
            loss = sum(during.filtered(
                lambda l: (l.doc_reference or "").startswith("DSP")).mapped("qty_out"))
            balance = opening + received - issued
            if not (opening or received or issued):
                continue
            price = card.product_id.standard_price or 0.0
            rows.append({
                "card": card,
                "po": card.purchase_order_id.name or card.po_reference or "",
                "receipt_date": min(during.mapped("date")) if during else "",
                "code": card.product_id.default_code or "",
                "name": card.product_id.name,
                "uom": card.uom_id.name or "",
                "opening": opening,
                "received": received,
                "issued": issued,
                "loss": loss,
                "balance": balance,
                "price": price,
                "total": balance * price,
                "location": card.location_id.complete_name or "",
                "lot": card.lot_id.name or "",
                "expiry": card.expiry_date or "",
                "remarks": "",
            })
        if not rows:
            raise UserError(_(
                "No stock movement was found in %(wh)s for %(month)s. Post a GSRN or a "
                "challan first.", wh=self.warehouse_id.display_name,
                month=self.month_date.strftime("%B %Y")))
        return rows

    def action_print_pdf(self):
        self.ensure_one()
        self._collect()
        return self.env.ref(
            "mcb_logistics.action_report_mcb_monthly_stock").report_action(self)

    def action_export_xlsx(self):
        self.ensure_one()
        rows = self._collect()
        headers = ["Sl No", "Waybill Number or PO Number", "Receipt Date", "Material Code",
                   "Material Description", "Unit of Measure", "Opening stock",
                   "Stock Received during the Month", "Stock issued Quantity during the Month",
                   "Loss/damage Quantity", "Stock Balance", "Unit Price BDT",
                   "Total Price BDT", "Location of stock Balance", "Batch No",
                   "Self life Expiry date", "Remarks"]
        data = []
        for i, r in enumerate(rows, start=1):
            data.append([i, r["po"], str(r["receipt_date"] or ""), r["code"], r["name"],
                         r["uom"], r["opening"], r["received"], r["issued"], r["loss"],
                         r["balance"], r["price"], r["total"], r["location"], r["lot"],
                         str(r["expiry"] or ""), r["remarks"]])
        total = sum(r["total"] for r in rows)
        return self._mcb_xlsx_download(
            filename=f"MCB_Monthly_Stock_{self.month_date.strftime('%Y_%m')}.xlsx",
            sheet_title=f"Monthly Stock Report {self.month_date.strftime('%B %Y')}",
            headers=headers, rows=data,
            footer_rows=[["", "", "", "", "TOTAL", "", "", "", "", "", "", "", total,
                          "", "", "", ""]])

    def _report_rows(self):
        return self._collect()
