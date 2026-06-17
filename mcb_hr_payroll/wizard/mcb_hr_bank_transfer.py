import base64
import csv
import io

from odoo import api, fields, models
from odoo.exceptions import UserError


class McbHrBankTransferWizard(models.TransientModel):
    """PAY-009 — Generate a bank disbursement CSV from a payslip batch.

    Produces a CSV with one row per payslip: employee name, account number,
    bank, branch, routing, net amount, and analytic / donor columns so the
    bank can route by project.
    """
    _name = "mcb.hr.bank.transfer.wizard"
    _description = "MCB Bank Disbursement File Generator"

    payslip_run_id = fields.Many2one("hr.payslip.run", required=True,
        default=lambda s: s.env.context.get("active_id")
            if s.env.context.get("active_model") == "hr.payslip.run" else False)
    bank_id = fields.Many2one("res.bank", string="Disbursement Bank",
        help="MCB's payroll bank (file destination).")
    transfer_date = fields.Date(default=fields.Date.context_today, required=True)

    file_data = fields.Binary(readonly=True, attachment=False)
    file_name = fields.Char(readonly=True)

    def action_generate(self):
        self.ensure_one()
        if not self.payslip_run_id.slip_ids:
            raise UserError("No payslips in this batch.")

        buf = io.StringIO()
        writer = csv.writer(buf, lineterminator="\n")
        writer.writerow([
            "Sequence", "Employee Code", "Employee Name",
            "Bank Account No", "Bank Name", "Branch",
            "Project Code", "Donor", "Analytic Code",
            "Net Amount (BDT)", "Currency",
        ])

        seq = 1
        total = 0.0
        for slip in self.payslip_run_id.slip_ids:
            net = sum(slip.line_ids.filtered(lambda l: l.code == "NET").mapped("total"))
            emp = slip.employee_id
            account = emp.bank_account_ids[:1] if hasattr(emp, "bank_account_ids") else False
            writer.writerow([
                seq,
                emp.mcb_employee_code or "",
                emp.name,
                account.acc_number if account else "",
                account.bank_id.name if account and account.bank_id else "",
                account.bank_id.bic if account and account.bank_id else "",
                slip.mcb_donor or emp.mcb_project_code or "",
                slip.mcb_donor or "",
                slip.mcb_analytic_code or "",
                round(net, 2),
                "BDT",
            ])
            seq += 1
            total += net

        writer.writerow([])
        writer.writerow(["", "", "TOTAL", "", "", "", "", "", "", round(total, 2), "BDT"])

        content = buf.getvalue().encode("utf-8")
        self.file_data = base64.b64encode(content)
        self.file_name = f"mcb_bank_disbursement_{self.payslip_run_id.name.replace('/', '_')}.csv"

        return {
            "type": "ir.actions.act_window",
            "res_model": "mcb.hr.bank.transfer.wizard",
            "view_mode": "form",
            "res_id": self.id,
            "target": "new",
            "name": "Bank Disbursement File",
        }
