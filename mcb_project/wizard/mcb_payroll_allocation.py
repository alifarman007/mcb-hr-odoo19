from dateutil.relativedelta import relativedelta

from odoo import fields, models, _
from odoo.exceptions import UserError


class McbPayrollAllocationWizard(models.TransientModel):
    """TMS-004 / PAY-010 (review finding 3) — posts a monthly journal entry that
    reallocates staff salary cost across project/donor analytic accounts according
    to the % assignments, so each donor's ledger carries its true staff cost."""
    _name = "mcb.payroll.allocation.wizard"
    _inherit = ["mcb.xlsx.mixin"]
    _description = "Monthly Payroll Cost Allocation (TMS-004)"

    month_date = fields.Date(
        required=True, string="Any date in the month",
        default=lambda s: fields.Date.context_today(s).replace(day=1))
    journal_id = fields.Many2one(
        "account.journal", domain="[('type', '=', 'general')]", required=True,
        default=lambda s: s.env["account.journal"].search(
            [("type", "=", "general"),
             ("company_id", "=", s.env.company.id)], limit=1))
    salary_account_id = fields.Many2one(
        "account.account", string="Salary Expense Account", required=True,
        domain="[('account_type', '=', 'expense')]")

    def _period(self):
        start = self.month_date.replace(day=1)
        end = start + relativedelta(months=1, days=-1)
        return start, end

    def _allocation_rows(self):
        start, end = self._period()
        assignments = self.env["mcb.project.assignment"].search([
            ("date_from", "<=", end), ("date_to", ">=", start),
            ("company_id", "=", self.env.company.id),
        ])
        rows = []
        for a in assignments:
            wage = a.employee_id.wage or 0.0
            amount = wage * a.percent / 100.0
            if amount and a.analytic_account_id:
                rows.append({
                    "employee": a.employee_id, "project": a.project_id,
                    "analytic": a.analytic_account_id,
                    "percent": a.percent, "wage": wage, "amount": amount,
                })
        return rows

    def action_post_allocation(self):
        self.ensure_one()
        rows = self._allocation_rows()
        if not rows:
            raise UserError(_("No project assignments found for this month (PRJ-005)."))
        start, end = self._period()
        lines = []
        total = 0.0
        for r in rows:
            lines.append((0, 0, {
                "account_id": self.salary_account_id.id,
                "name": _("%s — %s (%g%%)", r["employee"].name,
                          r["project"].name, r["percent"]),
                "debit": r["amount"],
                "analytic_distribution": {str(r["analytic"].id): 100},
            }))
            total += r["amount"]
        lines.append((0, 0, {
            "account_id": self.salary_account_id.id,
            "name": _("Payroll cost reallocated to projects %s", end.strftime("%b %Y")),
            "credit": total,
        }))
        move = self.env["account.move"].with_context(mcb_skip_approval=True).create({
            "move_type": "entry",
            "journal_id": self.journal_id.id,
            "date": end,
            "ref": _("Payroll cost allocation %s (TMS-004)", end.strftime("%b %Y")),
            "line_ids": lines,
        })
        move.action_post()
        return {"type": "ir.actions.act_window", "res_model": "account.move",
                "res_id": move.id, "view_mode": "form"}

    def action_export_xlsx(self):
        rows = [[r["employee"].name, r["project"].name, r["analytic"].name,
                 r["percent"], r["wage"], r["amount"]]
                for r in self._allocation_rows()]
        return self._mcb_xlsx_download(
            f"payroll_allocation_{self.month_date:%Y_%m}.xlsx",
            "Payroll Cost Allocation",
            ["Employee", "Project", "Analytic (Donor)", "% Time", "Monthly Wage",
             "Allocated Cost"],
            rows)
