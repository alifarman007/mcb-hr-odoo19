from datetime import timedelta

from odoo import api, fields, models
from odoo.exceptions import UserError


NOTICE_PERIODS = {
    "permanent": 60,
    "project": 30,
    "probationary": 15,
    "support": 30,
}


class McbHrResignation(models.Model):
    """SEP-001 … SEP-008 — Resignation / Separation workflow."""
    _name = "mcb.hr.resignation"
    _description = "MCB Resignation / Separation"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "submission_date desc"

    name = fields.Char(default="New", copy=False, readonly=True)
    employee_id = fields.Many2one(
        "hr.employee", required=True, ondelete="restrict", tracking=True,
        domain="[('active','=',True)]",
    )
    employment_type = fields.Selection(
        related="employee_id.mcb_employment_type", store=True, readonly=True,
    )
    submission_date = fields.Date(default=fields.Date.context_today, tracking=True)
    intended_last_day = fields.Date(string="Intended Last Working Day", tracking=True, required=True)
    required_notice_days = fields.Integer(
        compute="_compute_notice", store=True, string="Required Notice (days)",
    )
    actual_notice_days = fields.Integer(
        compute="_compute_notice", store=True, string="Actual Notice (days)",
    )
    notice_short_by_days = fields.Integer(
        compute="_compute_notice", store=True,
    )
    salary_in_lieu = fields.Monetary(
        compute="_compute_settlement", store=True, currency_field="currency_id",
        help="SEP-002 — salary in lieu of short-notice days.",
    )
    leave_encashment_days = fields.Float(
        help="SEP-004 — unused leave balance to encash.",
    )
    leave_encashment_amount = fields.Monetary(
        compute="_compute_settlement", store=True, currency_field="currency_id",
    )
    pf_entitlement = fields.Selection([
        ("own", "Own contribution only (<1 yr)"),
        ("own_employer", "Own + Employer (≥1 yr regular)"),
        ("forfeit_employer", "Forfeit employer (dismissal for misconduct)"),
    ], default="own", required=True,
        help="SEP-005 — PF entitlement on separation.")
    pf_amount = fields.Monetary(currency_field="currency_id",
        help="Stub field — final amount entered by Finance from PF Trust ledger.")
    gratuity_amount = fields.Monetary(currency_field="currency_id",
        help="SEP-004 — gratuity payout for ≥1yr permanent.")
    outstanding_salary = fields.Monetary(currency_field="currency_id")
    final_settlement_total = fields.Monetary(
        compute="_compute_settlement", store=True, currency_field="currency_id",
    )
    currency_id = fields.Many2one("res.currency", default=lambda s: s.env.company.currency_id)

    reason = fields.Selection([
        ("resign_voluntary", "Voluntary Resignation"),
        ("contract_end", "Contract End"),
        ("retirement", "Retirement"),
        ("termination", "Termination"),
        ("dismissal", "Dismissal"),
        ("death", "Death"),
    ], default="resign_voluntary", required=True, tracking=True)
    notes = fields.Html()
    state = fields.Selection([
        ("draft", "Draft"),
        ("submitted", "Submitted by Employee"),
        ("manager_review", "Line Manager Review"),
        ("hr_review", "HR Processing"),
        ("ce_approval", "CE Approval"),
        ("settled", "Settled"),
        ("closed", "Closed"),
        ("cancelled", "Cancelled"),
    ], default="draft", tracking=True, required=True)

    exit_interview_id = fields.Many2one("mcb.hr.exit.interview", string="Exit Interview")
    property_returned = fields.Boolean(string="Property / Equipment Returned (SEP-006)")
    account_deactivated = fields.Boolean(string="Odoo Account Deactivated (SEP-008)")
    experience_cert_issued = fields.Boolean(string="Experience Certificate Issued (SEP-007)")

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = self.env["ir.sequence"].next_by_code("mcb.hr.resignation") or "SEP/0000"
        return super().create(vals_list)

    @api.depends("submission_date", "intended_last_day", "employment_type")
    def _compute_notice(self):
        for rec in self:
            req = NOTICE_PERIODS.get(rec.employment_type or "project", 30)
            rec.required_notice_days = req
            if rec.submission_date and rec.intended_last_day:
                actual = (rec.intended_last_day - rec.submission_date).days
                rec.actual_notice_days = max(actual, 0)
                rec.notice_short_by_days = max(req - actual, 0)
            else:
                rec.actual_notice_days = 0
                rec.notice_short_by_days = 0

    @api.depends("notice_short_by_days", "leave_encashment_days", "outstanding_salary",
                 "pf_amount", "gratuity_amount", "employee_id")
    def _compute_settlement(self):
        for rec in self:
            wage = rec.employee_id.wage or 0
            daily_wage = wage / 30.0 if wage else 0.0
            rec.salary_in_lieu = daily_wage * rec.notice_short_by_days * -1.0  # deducted
            rec.leave_encashment_amount = daily_wage * (rec.leave_encashment_days or 0.0)
            rec.final_settlement_total = (
                (rec.outstanding_salary or 0)
                + rec.leave_encashment_amount
                + (rec.pf_amount or 0)
                + (rec.gratuity_amount or 0)
                + rec.salary_in_lieu  # negative if short notice
            )

    def action_submit(self):
        self.write({"state": "submitted"})

    def action_manager_review(self):
        self.write({"state": "manager_review"})

    def action_hr_process(self):
        self.write({"state": "hr_review"})

    def action_ce_approve(self):
        self.write({"state": "ce_approval"})

    def action_settle(self):
        for rec in self:
            if not rec.exit_interview_id:
                # Create stub exit interview
                rec.exit_interview_id = self.env["mcb.hr.exit.interview"].create({
                    "employee_id": rec.employee_id.id,
                    "resignation_id": rec.id,
                }).id
            rec.state = "settled"

    def action_close(self):
        for rec in self:
            # SEP-008 — deactivate Odoo user account
            if rec.employee_id.user_id:
                rec.employee_id.user_id.active = False
                rec.account_deactivated = True
            # archive employee
            rec.employee_id.active = False
            if rec.employee_id.departure_date is False or not rec.employee_id.departure_date:
                rec.employee_id.departure_date = rec.intended_last_day
            rec.state = "closed"

    def action_cancel(self):
        self.write({"state": "cancelled"})

    def action_print_experience_cert(self):
        self.experience_cert_issued = True
        return self.env.ref("mcb_hr_separation.action_report_mcb_experience_cert").report_action(self)
