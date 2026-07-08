from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class McbVolunteer(models.Model):
    """VOL-001 — HTV / RTV / community volunteer database."""
    _name = "mcb.volunteer"
    _description = "MCB Volunteer"
    _inherit = ["mail.thread"]
    _order = "name"

    name = fields.Char(required=True, tracking=True)
    camp_no = fields.Char(string="Camp Number", index=True)
    block = fields.Char(string="Block / Sub-block")
    phone = fields.Char()
    nid_or_reg = fields.Char(string="NID / FCN / Registration No", index=True)
    vol_type = fields.Selection([
        ("htv", "HTV (Host Trained Volunteer)"),
        ("rtv", "RTV (Rohingya Trained Volunteer)"),
        ("community", "Community Volunteer"),
    ], required=True, default="rtv", string="Volunteer Type", tracking=True)
    project_id = fields.Many2one("project.project", string="Project Assignment",
                                 tracking=True)
    joining_date = fields.Date()
    status = fields.Selection([
        ("active", "Active"), ("inactive", "Inactive"),
    ], default="active", tracking=True)
    payment_mode = fields.Selection([
        ("cash", "Cash"), ("bkash", "bKash / Mobile Banking"), ("bank", "Bank"),
    ], default="cash", string="Preferred Payment Mode")
    bkash_no = fields.Char(string="bKash / Wallet No")
    attendance_ids = fields.One2many("mcb.volunteer.attendance", "volunteer_id")
    company_id = fields.Many2one("res.company", default=lambda s: s.env.company)


class McbVolunteerAttendance(models.Model):
    """ATT-005 — volunteer daily attendance (HTV/RTV tracked separately by type)."""
    _name = "mcb.volunteer.attendance"
    _description = "MCB Volunteer Attendance"
    _order = "date desc"

    volunteer_id = fields.Many2one("mcb.volunteer", required=True, ondelete="cascade",
                                   index=True)
    date = fields.Date(required=True, default=fields.Date.context_today)
    present = fields.Boolean(default=True)
    project_id = fields.Many2one(related="volunteer_id.project_id", store=True)
    vol_type = fields.Selection(related="volunteer_id.vol_type", store=True)

    _sql_unique = models.Constraint(
        "unique(volunteer_id, date)",
        "One attendance record per volunteer per day.")


class McbVolunteerIncentiveBatch(models.Model):
    """VOL-002/003/004 — monthly incentive run: days present × category rate."""
    _name = "mcb.volunteer.incentive.batch"
    _description = "MCB Volunteer Incentive Batch"
    _inherit = ["mail.thread", "mcb.fy.mixin"]

    name = fields.Char(default="New", copy=False, readonly=True)
    month_date = fields.Date(
        required=True, string="Month",
        default=lambda s: fields.Date.context_today(s).replace(day=1))
    project_id = fields.Many2one("project.project", string="Project")
    rate_htv = fields.Monetary(string="Daily Rate — HTV", default=600,
                               currency_field="currency_id")
    rate_rtv = fields.Monetary(string="Daily Rate — RTV", default=500,
                               currency_field="currency_id")
    rate_community = fields.Monetary(string="Daily Rate — Community", default=400,
                                     currency_field="currency_id")
    line_ids = fields.One2many("mcb.volunteer.incentive.line", "batch_id")
    amount_total = fields.Monetary(compute="_compute_total", store=True,
                                   currency_field="currency_id")
    journal_id = fields.Many2one("account.journal", string="Pay From",
                                 domain="[('type', 'in', ('cash', 'bank'))]")
    expense_account_id = fields.Many2one(
        "account.account", string="Incentive Expense Account",
        domain="[('account_type', '=', 'expense')]")
    move_id = fields.Many2one("account.move", readonly=True, copy=False)
    currency_id = fields.Many2one("res.currency", default=lambda s: s.env.company.currency_id)
    company_id = fields.Many2one("res.company", default=lambda s: s.env.company)
    state = fields.Selection([
        ("draft", "Draft"),
        ("computed", "Computed"),
        ("approved", "Approved"),
        ("paid", "Paid / Posted"),
    ], default="draft", tracking=True)

    @api.depends("line_ids.amount")
    def _compute_total(self):
        for rec in self:
            rec.amount_total = sum(rec.line_ids.mapped("amount"))

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = self._mcb_fy_sequence_next("mcb.vol.incentive", "VIB")
        return super().create(vals_list)

    def _rate_for(self, vol):
        return {"htv": self.rate_htv, "rtv": self.rate_rtv,
                "community": self.rate_community}[vol.vol_type]

    def action_compute(self):
        """VOL-004 — attendance days × configured daily rate per category."""
        for rec in self:
            start = rec.month_date.replace(day=1)
            end = start + relativedelta(months=1, days=-1)
            domain = [("status", "=", "active")]
            if rec.project_id:
                domain.append(("project_id", "=", rec.project_id.id))
            rec.line_ids.unlink()
            for vol in self.env["mcb.volunteer"].search(domain):
                days = self.env["mcb.volunteer.attendance"].search_count([
                    ("volunteer_id", "=", vol.id), ("present", "=", True),
                    ("date", ">=", start), ("date", "<=", end)])
                if not days:
                    continue
                rec.line_ids = [(0, 0, {
                    "volunteer_id": vol.id,
                    "days_present": days,
                    "daily_rate": rec._rate_for(vol),
                    "payment_mode": vol.payment_mode,
                })]
            rec.state = "computed"

    def action_approve(self):
        self.write({"state": "approved"})

    def action_pay(self):
        """VOL-007 — one JE: Dr incentive expense (project analytic) / Cr cash-bank."""
        for rec in self:
            if not rec.journal_id or not rec.expense_account_id:
                raise UserError(_("Set the journal and incentive expense account."))
            if not rec.line_ids:
                raise UserError(_("Nothing to pay — compute the batch first."))
            analytic = rec.project_id.account_id if rec.project_id else False
            dist = {str(analytic.id): 100} if analytic else False
            move = self.env["account.move"].with_context(mcb_skip_approval=True).create({
                "move_type": "entry",
                "journal_id": rec.journal_id.id,
                "date": fields.Date.context_today(self),
                "ref": _("Volunteer incentives %s (%s)", rec.name,
                         rec.month_date.strftime("%b %Y")),
                "line_ids": [
                    (0, 0, {"account_id": rec.expense_account_id.id,
                            "name": _("Volunteer incentives %s",
                                      rec.month_date.strftime("%b %Y")),
                            "debit": rec.amount_total,
                            "analytic_distribution": dist}),
                    (0, 0, {"account_id": rec.journal_id.default_account_id.id,
                            "name": rec.name, "credit": rec.amount_total}),
                ],
            })
            move.action_post()
            rec.write({"move_id": move.id, "state": "paid"})


class McbVolunteerIncentiveLine(models.Model):
    _name = "mcb.volunteer.incentive.line"
    _description = "Volunteer Incentive Line"

    batch_id = fields.Many2one("mcb.volunteer.incentive.batch", required=True,
                               ondelete="cascade")
    volunteer_id = fields.Many2one("mcb.volunteer", required=True)
    camp_no = fields.Char(related="volunteer_id.camp_no", store=True)
    vol_type = fields.Selection(related="volunteer_id.vol_type", store=True)
    days_present = fields.Integer()
    daily_rate = fields.Monetary(currency_field="currency_id")
    amount = fields.Monetary(compute="_compute_amount", store=True,
                             currency_field="currency_id")
    payment_mode = fields.Selection([
        ("cash", "Cash"), ("bkash", "bKash"), ("bank", "Bank"),
    ], default="cash")
    currency_id = fields.Many2one(related="batch_id.currency_id")

    @api.depends("days_present", "daily_rate")
    def _compute_amount(self):
        for l in self:
            l.amount = l.days_present * l.daily_rate
