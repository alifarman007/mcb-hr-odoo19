from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError

# SRS Table-9 procurement method thresholds (BDT)
THRESHOLD_DIRECT = 10_000
THRESHOLD_RFQ = 200_000
THRESHOLD_RFP = 500_000


class McbPurchaseRequest(models.Model):
    """Step 1 — Purchase Request (PR-001..008) with Note Sheets 1–3."""
    _name = "mcb.purchase.request"
    _description = "MCB Purchase Request"
    _inherit = ["mail.thread", "mail.activity.mixin", "mcb.fy.mixin"]
    _order = "create_date desc"

    name = fields.Char(default="New", copy=False, readonly=True, index=True)
    requester_id = fields.Many2one("res.users", default=lambda s: s.env.user, tracking=True)
    date_request = fields.Date(default=fields.Date.context_today)
    company_id = fields.Many2one("res.company", default=lambda s: s.env.company, required=True)
    currency_id = fields.Many2one("res.currency", default=lambda s: s.env.company.currency_id)

    # PR-002 header fields
    project_analytic_id = fields.Many2one(
        "account.analytic.account", string="Project Name (Analytic)", required=True,
        tracking=True, help="PR-002/PR-007 — project analytic account for donor cost coding.")
    donor = fields.Char(string="Donor / Funder")
    budget_id = fields.Many2one("budget.analytic", string="Budget")
    budget_line_id = fields.Many2one(
        "budget.line", string="Budget Head & Code",
        domain="[('budget_analytic_id', '=', budget_id)]")
    total_budget = fields.Monetary(related="budget_line_id.budget_amount",
                                   string="Total Budget", currency_field="currency_id")
    current_balance = fields.Monetary(compute="_compute_balance",
                                      string="Current Balance", currency_field="currency_id")
    deadline = fields.Date(string="Procurement Deadline")
    delivery_point = fields.Char()
    contact_person = fields.Char()
    contact_phone = fields.Char()

    line_ids = fields.One2many("mcb.purchase.request.line", "request_id", string="Items")
    amount_total = fields.Monetary(compute="_compute_total", store=True,
                                   currency_field="currency_id", tracking=True)
    procurement_method = fields.Selection([
        ("direct", "Direct Purchase / Petty Cash (< 10,000)"),
        ("rfq", "RFQ (10,000 – 2,00,000)"),
        ("rfp", "RFP (2,00,001 – 5,00,000)"),
        ("ift", "IFT / Open Tender (> 5,00,000) — NOAL required"),
    ], compute="_compute_method", store=True, string="Procurement Method (Table-9)")
    noal_required = fields.Boolean(compute="_compute_method", store=True)
    min_quotations = fields.Integer(compute="_compute_method", store=True)

    # Note sheets (PR-006, steps 2 & 8)
    note1_html = fields.Html(string="Note Sheet-1 (CE instruction to PC)",
                             default=lambda s: _("Approved. Procurement Committee is "
                                                 "instructed to proceed as per guidelines."))
    note2_html = fields.Html(string="Note Sheet-2 (PC minutes)")
    note3_html = fields.Html(string="Note Sheet-3 (Award recommendation)")

    # PR-005 approvals
    accounts_officer_id = fields.Many2one("res.users", readonly=True, copy=False,
                                          string="Accounts Officer")
    pc_incharge_id = fields.Many2one("res.users", readonly=True, copy=False,
                                     string="PC / In-charge")
    ce_id = fields.Many2one("res.users", readonly=True, copy=False, string="CE")
    budget_override = fields.Boolean(
        string="CE Budget Override", tracking=True,
        help="PR-004 — allows submission above current budget balance (CE only).")

    # PR-008 status flow
    state = fields.Selection([
        ("draft", "Draft"),
        ("confirmed", "Confirmed"),
        ("accounts", "Accounts Checked"),
        ("approved", "Approved (CE)"),
        ("sent_pc", "Sent to PC"),
        ("in_progress", "In Progress"),
        ("po_issued", "PO Issued"),
        ("closed", "Closed"),
        ("cancelled", "Cancelled"),
    ], default="draft", tracking=True)

    order_ids = fields.One2many("purchase.order", "mcb_pr_id", string="RFQs / POs")
    order_count = fields.Integer(compute="_compute_order_count")

    # step timestamps for the PR Process Report (Table-14)
    date_confirmed = fields.Datetime(readonly=True, copy=False)
    date_approved = fields.Datetime(readonly=True, copy=False)
    date_sent_pc = fields.Datetime(readonly=True, copy=False)
    date_po_issued = fields.Datetime(readonly=True, copy=False)

    @api.depends("line_ids.price_total")
    def _compute_total(self):
        for rec in self:
            rec.amount_total = sum(rec.line_ids.mapped("price_total"))

    @api.depends("amount_total")
    def _compute_method(self):
        for rec in self:
            amt = rec.amount_total
            if amt < THRESHOLD_DIRECT:
                rec.procurement_method, rec.min_quotations = "direct", 1
            elif amt <= THRESHOLD_RFQ:
                rec.procurement_method, rec.min_quotations = "rfq", 3
            elif amt <= THRESHOLD_RFP:
                rec.procurement_method, rec.min_quotations = "rfp", 3
            else:
                rec.procurement_method, rec.min_quotations = "ift", 3
            rec.noal_required = rec.procurement_method == "ift"

    def _compute_balance(self):
        for rec in self:
            if rec.budget_line_id:
                rec.current_balance = (rec.budget_line_id.budget_amount
                                       - rec.budget_line_id.achieved_amount)
            else:
                rec.current_balance = 0.0

    def _compute_order_count(self):
        for rec in self:
            rec.order_count = len(rec.order_ids)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                # PR-001 — PR: XXXX/YY-YY per financial year
                fy = self._mcb_fy_label()
                num = self._mcb_fy_sequence_next("mcb.pr", "PRN", padding=4).split("-")[-1]
                vals["name"] = f"PR: {num}/{fy}"
        return super().create(vals_list)

    # ---- PR-004 budget validation ----
    def _check_budget(self):
        for rec in self:
            if not rec.budget_line_id:
                continue
            if rec.amount_total > rec.current_balance and not rec.budget_override:
                raise ValidationError(_(
                    "PR-004 — PR total %(tot).2f exceeds the current budget balance "
                    "%(bal).2f of head '%(head)s'. A CE budget override is required.",
                    tot=rec.amount_total, bal=rec.current_balance,
                    head=rec.budget_line_id.display_name))

    # ---- PR-005 workflow ----
    def action_confirm(self):
        for rec in self:
            if not rec.line_ids:
                raise UserError(_("Add at least one item line (PR-003)."))
        self._check_budget()
        self.write({"state": "confirmed", "date_confirmed": fields.Datetime.now()})

    def action_accounts_check(self):
        self.write({"state": "accounts", "accounts_officer_id": self.env.user.id})

    def action_ce_approve(self):
        for rec in self:
            rec._check_budget()
        self.write({"state": "approved", "ce_id": self.env.user.id,
                    "date_approved": fields.Datetime.now()})

    def action_send_pc(self):
        self.write({"state": "sent_pc", "pc_incharge_id": self.env.user.id,
                    "date_sent_pc": fields.Datetime.now()})

    def action_cancel(self):
        self.write({"state": "cancelled"})

    def action_close(self):
        self.write({"state": "closed"})

    # ---- Step 3: generate RFQs (one draft PO per vendor) ----
    def action_create_rfqs(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "res_model": "mcb.pr.rfq.wizard",
            "view_mode": "form",
            "target": "new",
            "context": {"default_request_id": self.id},
        }

    def action_view_orders(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": _("RFQs / POs"),
            "res_model": "purchase.order",
            "view_mode": "list,form",
            "domain": [("mcb_pr_id", "=", self.id)],
        }


class McbPurchaseRequestLine(models.Model):
    _name = "mcb.purchase.request.line"
    _description = "MCB PR Item Line (PR-003)"

    request_id = fields.Many2one("mcb.purchase.request", required=True, ondelete="cascade")
    product_id = fields.Many2one("product.product", string="Product (optional)")
    name = fields.Char(string="Name of Items", required=True)
    specification = fields.Text(string="Specifications")
    category = fields.Char()
    uom_id = fields.Many2one("uom.uom", string="M. Unit")
    quantity = fields.Float(default=1, required=True)
    price_unit = fields.Monetary(string="Unit Price (est.)", currency_field="currency_id")
    price_total = fields.Monetary(compute="_compute_total", store=True,
                                  currency_field="currency_id")
    currency_id = fields.Many2one(related="request_id.currency_id")

    @api.depends("quantity", "price_unit")
    def _compute_total(self):
        for l in self:
            l.price_total = l.quantity * l.price_unit

    @api.onchange("product_id")
    def _onchange_product(self):
        for l in self:
            if l.product_id:
                l.name = l.product_id.display_name
                l.uom_id = l.product_id.uom_id
                l.price_unit = l.product_id.standard_price


class McbPrRfqWizard(models.TransientModel):
    """Create one draft RFQ (purchase.order) per selected vendor from the PR."""
    _name = "mcb.pr.rfq.wizard"
    _description = "Generate RFQs from PR"

    request_id = fields.Many2one("mcb.purchase.request", required=True)
    vendor_ids = fields.Many2many("res.partner", string="Vendors",
                                  domain="[('supplier_rank', '>=', 0)]")

    def action_generate(self):
        self.ensure_one()
        pr = self.request_id
        if len(self.vendor_ids) < pr.min_quotations and pr.procurement_method != "direct":
            raise UserError(_(
                "Table-9 — the %(m)s method requires at least %(n)d quotations.",
                m=pr.procurement_method.upper(), n=pr.min_quotations))
        product_fallback = self.env.ref("mcb_purchase.product_mcb_generic",
                                        raise_if_not_found=False)
        orders = self.env["purchase.order"]
        dist = {str(pr.project_analytic_id.id): 100} if pr.project_analytic_id else False
        for vendor in self.vendor_ids:
            lines = []
            for l in pr.line_ids:
                product = l.product_id or product_fallback
                lines.append((0, 0, {
                    "product_id": product.id,
                    "name": f"{l.name}\n{l.specification or ''}".strip(),
                    "product_qty": l.quantity,
                    "price_unit": l.price_unit,
                    "analytic_distribution": dist,
                }))
            orders |= self.env["purchase.order"].create({
                "partner_id": vendor.id,
                "mcb_pr_id": pr.id,
                "origin": pr.name,
                "order_line": lines,
            })
        pr.state = "in_progress"
        return pr.action_view_orders()
