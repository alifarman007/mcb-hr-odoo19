import io

from odoo import api, models, fields


class McbFyMixin(models.AbstractModel):
    """July–June Bangladesh fiscal-year helpers (PER-005).

    FY label format YY-YY (e.g. 25-26) and compact YYYY (2526) for sequences.
    """
    _name = "mcb.fy.mixin"
    _description = "MCB Fiscal Year Helpers"

    @api.model
    def _mcb_fy_bounds(self, on_date=None):
        d = on_date or fields.Date.context_today(self)
        if d.month >= 7:
            start = d.replace(month=7, day=1)
            end = d.replace(year=d.year + 1, month=6, day=30)
        else:
            start = d.replace(year=d.year - 1, month=7, day=1)
            end = d.replace(month=6, day=30)
        return start, end

    @api.model
    def _mcb_fy_label(self, on_date=None, compact=False):
        start, end = self._mcb_fy_bounds(on_date)
        y1, y2 = start.year % 100, end.year % 100
        return f"{y1:02d}{y2:02d}" if compact else f"{y1:02d}-{y2:02d}"

    @api.model
    def _mcb_fy_sequence_next(self, code, prefix, on_date=None, padding=3):
        """Next number from a per-FY sequence, creating the sequence on first use."""
        fy = self._mcb_fy_label(on_date, compact=True)
        full_code = f"{code}.{fy}"
        seq = self.env["ir.sequence"].sudo().search([("code", "=", full_code)], limit=1)
        if not seq:
            seq = self.env["ir.sequence"].sudo().create({
                "name": f"{prefix} {fy}",
                "code": full_code,
                "prefix": f"{prefix}-{fy}-",
                "padding": padding,
            })
        return seq.next_by_id()


class McbXlsxMixin(models.AbstractModel):
    """Shared XLSX builder: rows → attachment → download action (client feedback VOU-006 etc.)."""
    _name = "mcb.xlsx.mixin"
    _description = "MCB XLSX Export Helper"

    def _mcb_xlsx_download(self, filename, sheet_title, headers, rows, footer_rows=None):
        import xlsxwriter

        buf = io.BytesIO()
        wb = xlsxwriter.Workbook(buf, {"in_memory": True})
        ws = wb.add_worksheet(sheet_title[:31])
        h_fmt = wb.add_format({"bold": True, "bg_color": "#1F4E79", "font_color": "white",
                               "border": 1})
        c_fmt = wb.add_format({"border": 1})
        t_fmt = wb.add_format({"bold": True, "border": 1})
        title_fmt = wb.add_format({"bold": True, "font_size": 14})
        ws.write(0, 0, "Mukti Cox's Bazar", title_fmt)
        ws.write(1, 0, sheet_title)
        row_i = 3
        for col, h in enumerate(headers):
            ws.write(row_i, col, h, h_fmt)
            ws.set_column(col, col, max(12, min(40, len(str(h)) + 4)))
        for r in rows:
            row_i += 1
            for col, val in enumerate(r):
                ws.write(row_i, col, val if val is not None else "", c_fmt)
        for fr in (footer_rows or []):
            row_i += 1
            for col, val in enumerate(fr):
                ws.write(row_i, col, val if val is not None else "", t_fmt)
        wb.close()
        att = self.env["ir.attachment"].create({
            "name": filename,
            "datas": __import__("base64").b64encode(buf.getvalue()),
            "res_model": self._name,
            "res_id": self.id if self.ids else 0,
            "mimetype": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        })
        return {
            "type": "ir.actions.act_url",
            "url": f"/web/content/{att.id}?download=true",
            "target": "self",
        }
