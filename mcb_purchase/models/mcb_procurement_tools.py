from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class McbOpeningSheet(models.Model):
    """Step 4 — RFQ/Tender Opening Sheet."""
    _name = "mcb.opening.sheet"
    _description = "MCB RFQ/Tender Opening Sheet"
    _inherit = ["mail.thread", "mcb.fy.mixin"]

    name = fields.Char(default="New", copy=False, readonly=True)
    request_id = fields.Many2one("mcb.purchase.request", required=True, string="PR")
    opening_datetime = fields.Datetime(default=fields.Datetime.now, required=True)
    member_ids = fields.Many2many("res.users", string="Committee Members Present")
    line_ids = fields.One2many("mcb.opening.sheet.line", "sheet_id", string="Bidders")
    state = fields.Selection([("draft", "Draft"), ("done", "Recorded")],
                             default="draft", tracking=True)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = self._mcb_fy_sequence_next("mcb.opening.sheet", "OPS")
        return super().create(vals_list)

    def action_fill_bidders(self):
        for rec in self:
            existing = rec.line_ids.mapped("vendor_id")
            for po in rec.request_id.order_ids:
                if po.partner_id not in existing:
                    rec.line_ids = [(0, 0, {
                        "vendor_id": po.partner_id.id,
                        "quoted_total": po.amount_total,
                    })]

    def action_done(self):
        self.write({"state": "done"})


class McbOpeningSheetLine(models.Model):
    _name = "mcb.opening.sheet.line"
    _description = "Opening Sheet Bidder Line"

    sheet_id = fields.Many2one("mcb.opening.sheet", required=True, ondelete="cascade")
    vendor_id = fields.Many2one("res.partner", required=True, string="Bidder")
    quoted_total = fields.Float(string="Quoted Total (BDT)")
    security_submitted = fields.Boolean(string="Security Money Submitted")
    remarks = fields.Char()


class McbTechnicalAnalysis(models.Model):
    """Step 5 — Technical Analysis TA-1 (RFQ/RFP) / TA-2 (Tender). Gate for CS-005."""
    _name = "mcb.technical.analysis"
    _description = "MCB Technical Analysis (TA-1 / TA-2)"
    _inherit = ["mail.thread", "mcb.fy.mixin"]

    name = fields.Char(default="New", copy=False, readonly=True)
    request_id = fields.Many2one("mcb.purchase.request", required=True, string="PR")
    ta_type = fields.Selection([("ta1", "TA-1 (RFQ/RFP)"), ("ta2", "TA-2 (Tender)")],
                               default="ta1", required=True)
    line_ids = fields.One2many("mcb.technical.analysis.line", "analysis_id")
    state = fields.Selection([("draft", "Draft"), ("done", "Completed")],
                             default="draft", tracking=True)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = self._mcb_fy_sequence_next("mcb.technical.analysis", "TA")
        return super().create(vals_list)

    def action_fill_vendors(self):
        for rec in self:
            existing = rec.line_ids.mapped("vendor_id")
            for po in rec.request_id.order_ids:
                if po.partner_id not in existing:
                    rec.line_ids = [(0, 0, {"vendor_id": po.partner_id.id})]

    def action_done(self):
        self.write({"state": "done"})

    def passed_vendors(self):
        self.ensure_one()
        return self.line_ids.filtered(lambda l: l.result == "pass").mapped("vendor_id")


class McbTechnicalAnalysisLine(models.Model):
    _name = "mcb.technical.analysis.line"
    _description = "Technical Analysis Vendor Line"

    analysis_id = fields.Many2one("mcb.technical.analysis", required=True, ondelete="cascade")
    vendor_id = fields.Many2one("res.partner", required=True, string="Vendor")
    spec_compliance = fields.Boolean(string="Meets Specifications")
    delivery_compliance = fields.Boolean(string="Meets Delivery Requirements")
    result = fields.Selection([("pass", "Pass"), ("fail", "Fail")], default="pass",
                              required=True)
    remarks = fields.Char()


class McbComparativeStatement(models.Model):
    """Step 6 — Comparative Statement (CS-001..008)."""
    _name = "mcb.comparative.statement"
    _description = "MCB Comparative Statement"
    _inherit = ["mail.thread", "mcb.fy.mixin"]

    name = fields.Char(default="New", copy=False, readonly=True)
    request_id = fields.Many2one("mcb.purchase.request", required=True, string="PR Ref")
    project_analytic_id = fields.Many2one(related="request_id.project_analytic_id",
                                          store=True)
    donor = fields.Char(related="request_id.donor", store=True)
    circular_date = fields.Date(string="Circular / Tender Date")
    opening_date = fields.Date()
    evaluation_date = fields.Date(default=fields.Date.context_today)
    technical_analysis_id = fields.Many2one("mcb.technical.analysis",
                                            string="Technical Analysis (CS-005)")
    vendor_line_ids = fields.One2many("mcb.cs.vendor", "cs_id", string="Vendors")
    pc_comment = fields.Html(string="Procurement Committee Comment (CS-006)")
    state = fields.Selection([("draft", "Draft"), ("done", "Finalised")],
                             default="draft", tracking=True)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = self._mcb_fy_sequence_next("mcb.cs", "CS")
        return super().create(vals_list)

    def action_fill_vendors(self):
        """Pull TA-passed vendors' RFQs into vendor columns (CS-002/003/005)."""
        for rec in self:
            passed = (rec.technical_analysis_id.passed_vendors()
                      if rec.technical_analysis_id else
                      rec.request_id.order_ids.mapped("partner_id"))
            rec.vendor_line_ids.unlink()
            for po in rec.request_id.order_ids:
                if po.partner_id in passed:
                    rec.vendor_line_ids = [(0, 0, {
                        "vendor_id": po.partner_id.id,
                        "order_id": po.id,
                        "grand_total": po.amount_total,
                    })]
            rec._rank()

    def _rank(self):
        """CS-004 — 1st/2nd/3rd lowest bidding positions."""
        for rec in self:
            for pos, line in enumerate(
                    rec.vendor_line_ids.sorted(key=lambda l: l.grand_total), start=1):
                line.position = pos

    @api.constrains("vendor_line_ids")
    def _check_ta_passed(self):
        for rec in self:
            if not rec.technical_analysis_id:
                continue
            passed = rec.technical_analysis_id.passed_vendors()
            for line in rec.vendor_line_ids:
                if line.vendor_id not in passed:
                    raise ValidationError(_(
                        "CS-005 — vendor '%s' has not passed the Technical Analysis "
                        "and cannot appear on the Comparative Statement.",
                        line.vendor_id.name))

    def action_done(self):
        for rec in self:
            if len(rec.vendor_line_ids) < rec.request_id.min_quotations:
                raise UserError(_(
                    "CS-002 — minimum %d technically-qualified quotations required.",
                    rec.request_id.min_quotations))
            rec._rank()
        self.write({"state": "done"})


class McbCsVendor(models.Model):
    _name = "mcb.cs.vendor"
    _description = "CS Vendor Column"
    _order = "position, id"

    cs_id = fields.Many2one("mcb.comparative.statement", required=True, ondelete="cascade")
    vendor_id = fields.Many2one("res.partner", required=True, string="Supplier")
    order_id = fields.Many2one("purchase.order", string="RFQ")
    grand_total = fields.Float(string="Grand Total (CS-003)")
    position = fields.Integer(string="Bidding Position (CS-004)")


class McbVendorEvaluation(models.Model):
    """Step 7 — Evaluation Report (Eval-1 / Eval-2)."""
    _name = "mcb.vendor.evaluation"
    _description = "MCB Vendor Evaluation Report"
    _inherit = ["mail.thread", "mcb.fy.mixin"]

    name = fields.Char(default="New", copy=False, readonly=True)
    request_id = fields.Many2one("mcb.purchase.request", required=True, string="PR")
    cs_id = fields.Many2one("mcb.comparative.statement", string="Comparative Statement")
    eval_type = fields.Selection([("eval1", "Eval-1 (RFQ/RFP)"), ("eval2", "Eval-2 (Tender)")],
                                 default="eval1", required=True)
    line_ids = fields.One2many("mcb.vendor.evaluation.line", "evaluation_id")
    recommended_vendor_id = fields.Many2one("res.partner", string="Recommended Vendor",
                                            tracking=True)
    state = fields.Selection([("draft", "Draft"), ("done", "Approved")],
                             default="draft", tracking=True)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = self._mcb_fy_sequence_next("mcb.vendor.eval", "EVAL")
        return super().create(vals_list)

    def action_done(self):
        for rec in self:
            if not rec.recommended_vendor_id:
                best = rec.line_ids.sorted(key=lambda l: -l.total_score)[:1]
                rec.recommended_vendor_id = best.vendor_id
        self.write({"state": "done"})

    def action_create_po(self):
        """PO-001 — populate the winning PO from the evaluation and mark the others lost."""
        self.ensure_one()
        if self.state != "done" or not self.recommended_vendor_id:
            raise UserError(_("Approve the evaluation with a recommended vendor first."))
        winner = self.request_id.order_ids.filtered(
            lambda o: o.partner_id == self.recommended_vendor_id and o.state == "draft")[:1]
        if not winner:
            raise UserError(_("No draft RFQ found for the recommended vendor."))
        winner.mcb_evaluation_id = self.id
        # NOAL-001 — auto-create draft NOAL when the value demands it
        if self.request_id.noal_required and not winner.mcb_noal_id:
            noal = self.env["mcb.noal"].create({
                "order_id": winner.id,
                "vendor_id": winner.partner_id.id,
                "contract_price": winner.amount_total,
            })
            winner.mcb_noal_id = noal.id
        self.request_id.state = "in_progress"
        return {
            "type": "ir.actions.act_window",
            "res_model": "purchase.order",
            "res_id": winner.id,
            "view_mode": "form",
        }


class McbVendorEvaluationLine(models.Model):
    _name = "mcb.vendor.evaluation.line"
    _description = "Vendor Evaluation Criteria Line"

    evaluation_id = fields.Many2one("mcb.vendor.evaluation", required=True,
                                    ondelete="cascade")
    vendor_id = fields.Many2one("res.partner", required=True, string="Vendor")
    price_score = fields.Float(string="Price (40)")
    quality_score = fields.Float(string="Quality/Spec (30)")
    delivery_score = fields.Float(string="Delivery (15)")
    experience_score = fields.Float(string="Experience (15)")
    total_score = fields.Float(compute="_compute_total", store=True)

    @api.depends("price_score", "quality_score", "delivery_score", "experience_score")
    def _compute_total(self):
        for l in self:
            l.total_score = (l.price_score + l.quality_score
                             + l.delivery_score + l.experience_score)


class McbProcurementChecklist(models.Model):
    """Annexure-29 — Checklist for Procurement Procedures."""
    _name = "mcb.procurement.checklist"
    _description = "MCB Procurement Checklist (Annexure-29)"
    _inherit = ["mail.thread"]

    name = fields.Char(default="New", copy=False, readonly=True)
    request_id = fields.Many2one("mcb.purchase.request", required=True, string="PR")
    order_id = fields.Many2one("purchase.order", string="PO")
    line_ids = fields.One2many("mcb.procurement.checklist.line", "checklist_id")
    state = fields.Selection([("draft", "Draft"), ("done", "Verified")],
                             default="draft", tracking=True)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = self.env["ir.sequence"].next_by_code(
                    "mcb.procurement.checklist") or "PCC/000"
        records = super().create(vals_list)
        template_items = self.env["mcb.checklist.item.template"].search(
            [("checklist_type", "=", "procurement")], order="sequence")
        for rec in records:
            if not rec.line_ids and template_items:
                rec.line_ids = [(0, 0, {"name": t.name, "sequence": t.sequence})
                                for t in template_items]
        return records

    def action_done(self):
        self.write({"state": "done"})


class McbProcurementChecklistLine(models.Model):
    _name = "mcb.procurement.checklist.line"
    _description = "Procurement Checklist Line"
    _order = "sequence, id"

    checklist_id = fields.Many2one("mcb.procurement.checklist", required=True,
                                   ondelete="cascade")
    sequence = fields.Integer(default=10)
    name = fields.Char(string="Particulars", required=True)
    status = fields.Selection([("yes", "Yes"), ("no", "No"), ("na", "N/A")], default="na")
    remarks = fields.Char()
