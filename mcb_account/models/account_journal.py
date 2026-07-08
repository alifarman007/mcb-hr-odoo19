from odoo import fields, models


class AccountJournal(models.Model):
    _inherit = "account.journal"

    mcb_require_approval = fields.Boolean(
        string="MCB 4-Level Voucher Approval",
        help="VOU-002 — entries in this journal cannot be posted until Checked, "
             "Reviewed and Approved (Prepared = creator).",
    )
    mcb_petty_cash_limit = fields.Monetary(
        string="Petty Cash Limit",
        currency_field="currency_id",
        help="PCH-005 — configured float for this cash journal; alert below 20%.",
    )


class AccountJournalStaleCheque(models.Model):
    _inherit = "account.journal"

    def _cron_mcb_stale_cheque_alert(self):
        """BNK-006 — alert Finance for cheques outstanding more than 30 days."""
        from datetime import timedelta
        cutoff = fields.Date.context_today(self) - timedelta(days=30)
        for journal in self.search([("type", "=", "bank")]):
            outstanding_accounts = (
                journal.company_id.account_journal_payment_credit_account_id
            )
            if not outstanding_accounts:
                continue
            stale = self.env["account.move.line"].search([
                ("journal_id", "=", journal.id),
                ("account_id", "in", outstanding_accounts.ids),
                ("credit", ">", 0),
                ("date", "<", cutoff),
                ("parent_state", "=", "posted"),
                ("full_reconcile_id", "=", False),
            ], limit=50)
            if not stale:
                continue
            already = self.env["mail.activity"].search_count([
                ("res_model", "=", "account.journal"), ("res_id", "=", journal.id),
                ("summary", "like", "BNK-006")], limit=1)
            if already:
                continue
            manager_group = self.env.ref("account.group_account_manager")
            user = manager_group.users[:1] or self.env.ref("base.user_admin")
            self.env["mail.activity"].create({
                "res_model_id": self.env["ir.model"]._get_id("account.journal"),
                "res_id": journal.id,
                "activity_type_id": self.env.ref("mail.mail_activity_data_todo").id,
                "user_id": user.id,
                "summary": "BNK-006 — cheques outstanding > 30 days (%s)" % journal.name,
                "note": ", ".join(
                    f"{l.date} {l.payment_id.check_number or l.name or ''} "
                    f"({l.partner_id.name or '-'}: {l.credit:.2f})"
                    for l in stale[:15]),
            })
