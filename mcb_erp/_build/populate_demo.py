"""
Master demo-data population script for the MCB ERP tutorial screenshots.
Run via:
  ./venv/bin/python ./odoo/odoo-bin shell -c ./odoo.conf -d mcb_demo --no-http < this_file

Drives every workflow through its REAL action_* methods (not just state writes)
so approvals, journal entries and computed fields all look correct on screen.
Persists (no rollback) — this becomes the permanent demo story for the tutorials.
"""
import traceback
from datetime import date, timedelta

env = env  # noqa: F821
today = date.today()
CO1 = 1
RESULTS = []


def run(name, fn):
    try:
        out = fn()
        RESULTS.append((name, "OK", ""))
        print(f"OK   {name}")
        return out
    except Exception as e:
        RESULTS.append((name, "FAIL", str(e)))
        print(f"FAIL {name}: {e}")
        traceback.print_exc()
        return None


# =====================================================================
# 0. GRANT ADMIN ALL MCB GROUPS
# =====================================================================
def _grant_groups():
    admin = env.ref("base.user_admin")
    for xmlid in [
        "mcb_hr_employee.group_mcb_ce",
        "mcb_hr_employee.group_mcb_pm",
        "mcb_hr_employee.group_mcb_rc",
        "mcb_account.group_mcb_finance_manager",
        "mcb_purchase.group_mcb_proc_manager",
    ]:
        grp = env.ref(xmlid, raise_if_not_found=False)
        if grp:
            admin.write({"groups_id": [(4, grp.id)]})
    return "granted"


run("grant admin groups", _grant_groups)
env.cr.commit()

Employee = env["hr.employee"]
emp_rashed = Employee.search([("name", "=", "Rashedul Karim")], limit=1)
emp_farzana = Employee.search([("name", "=", "Farzana Akter")], limit=1)
emp_aminul = Employee.search([("name", "=", "Aminul Haque")], limit=1)

gbvie = env["project.project"].browse(10)
analytic_gbvie = gbvie.account_id
analytic_care = env["account.analytic.account"].search([("name", "=", "GBViE-CARE")], limit=1)
analytic_unfpa = env["account.analytic.account"].search([("name", "=", "FDMN-UNFPA")], limit=1)

bank_j = env["account.journal"].search([("type", "=", "bank"), ("company_id", "=", CO1)], limit=1)
general_j = env["account.journal"].search(
    [("type", "=", "general"), ("company_id", "=", CO1), ("name", "=", "Miscellaneous Operations")], limit=1)
expense_acc = env["account.account"].search([("code", "=", "600000"), ("company_ids", "in", CO1)], limit=1)
liability_acc = env["account.account"].search([("code", "=", "201000"), ("company_ids", "in", CO1)], limit=1)
income_acc = env["account.account"].search([("account_type", "=", "income"), ("company_ids", "in", CO1)], limit=1)

print("refs:", emp_rashed, emp_farzana, gbvie, analytic_care, analytic_unfpa, bank_j, general_j)

# =====================================================================
# PART B — PURCHASE / PROCUREMENT
# =====================================================================
Vendor = env["res.partner"]
vendor1 = Vendor.search([("name", "=", "Gemini Furniture")], limit=1)
vendor2 = Vendor.search([("name", "=", "Ready Mat")], limit=1)
vendor3 = run("create vendor3", lambda: Vendor.create({
    "name": "Modern Furnishing BD", "supplier_rank": 1, "is_company": True}))
vendor4 = run("create vendor4 (civil)", lambda: Vendor.create({
    "name": "BD Builders Ltd", "supplier_rank": 1, "is_company": True}))
vendor5 = run("create vendor5 (civil)", lambda: Vendor.create({
    "name": "Coxs Bazar Construction Co", "supplier_rank": 1, "is_company": True}))

PR = env["mcb.purchase.request"]

# --- PR1: existing demo PR (RFP band) -> drive full pipeline to a confirmed PO
pr1 = PR.browse(1)


def _drive_pr1():
    if pr1.state == "draft":
        pr1.action_confirm()
    if pr1.state == "confirmed":
        pr1.action_accounts_check()
    if pr1.state == "accounts":
        pr1.action_ce_approve()
    if pr1.state == "approved":
        pr1.action_send_pc()
    wiz = env["mcb.pr.rfq.wizard"].create({
        "request_id": pr1.id,
        "vendor_ids": [(6, 0, [vendor1.id, vendor2.id, vendor3.id])],
    })
    wiz.action_generate()
    return pr1.state


run("PR1 drive to in_progress + RFQs", _drive_pr1)

opening1 = run("PR1 opening sheet", lambda: env["mcb.opening.sheet"].create({
    "request_id": pr1.id,
    "member_ids": [(6, 0, [env.ref("base.user_admin").id])],
}))
if opening1:
    run("PR1 opening: fill bidders", opening1.action_fill_bidders)
    run("PR1 opening: done", opening1.action_done)

ta1 = run("PR1 technical analysis", lambda: env["mcb.technical.analysis"].create({
    "request_id": pr1.id, "ta_type": "ta1",
}))
if ta1:
    run("PR1 TA: fill vendors", ta1.action_fill_vendors)
    ta1.line_ids.write({"spec_compliance": True, "delivery_compliance": True, "result": "pass"})
    run("PR1 TA: done", ta1.action_done)

cs1 = run("PR1 comparative statement", lambda: env["mcb.comparative.statement"].create({
    "request_id": pr1.id,
    "technical_analysis_id": ta1.id if ta1 else False,
    "circular_date": today - timedelta(days=20),
    "opening_date": today - timedelta(days=10),
    "pc_comment": "<p>All three quotations are technically compliant. "
                  "M/S Gemini Furniture offers the lowest total price with acceptable "
                  "delivery timeline. Recommended for award.</p>",
}))
if cs1:
    run("PR1 CS: fill vendors", cs1.action_fill_vendors)
    run("PR1 CS: done", cs1.action_done)

eval1 = run("PR1 evaluation", lambda: env["mcb.vendor.evaluation"].create({
    "request_id": pr1.id, "cs_id": cs1.id if cs1 else False, "eval_type": "eval1",
}))
if eval1:
    for line in eval1.line_ids:
        pass
    # build score lines manually from CS vendors
    if not eval1.line_ids:
        for v in cs1.vendor_line_ids.mapped("vendor_id"):
            env["mcb.vendor.evaluation.line"].create({
                "evaluation_id": eval1.id, "vendor_id": v.id,
                "price_score": 35 if v == vendor1 else 28,
                "quality_score": 27, "delivery_score": 13, "experience_score": 12,
            })
    eval1.recommended_vendor_id = vendor1.id
    run("PR1 evaluation: done", eval1.action_done)
    po1 = run("PR1 evaluation: create PO", eval1.action_create_po)

po1_final = env["purchase.order"].search([("mcb_pr_id", "=", pr1.id), ("state", "=", "draft")], limit=1)
if po1_final:
    def _confirm_po1():
        po1_final.action_mcb_check()
        po1_final.action_mcb_review()
        po1_final.action_mcb_approve()
        po1_final.button_confirm()
        return po1_final.state
    run("PR1 PO: 4-level approve + confirm", _confirm_po1)

checklist1 = run("PR1 procurement checklist", lambda: env["mcb.procurement.checklist"].create({
    "request_id": pr1.id, "order_id": po1_final.id if po1_final else False,
}))
if checklist1:
    for l in checklist1.line_ids[:10]:
        l.status = "yes"
    run("PR1 checklist: done", checklist1.action_done)


# --- PR2: big-ticket IFT/tender -> demonstrates NOAL gate
pr2 = run("create PR2 (IFT/civil works)", lambda: PR.create({
    "project_analytic_id": analytic_gbvie.id,
    "donor": "CARE",
    "delivery_point": "GBViE Camp 12 Learning Centre",
    "contact_person": "Site Engineer",
    "contact_phone": "+8801700000001",
    "line_ids": [(0, 0, {
        "name": "Civil works — renovation of camp learning centre",
        "specification": "Roof repair, flooring, electrical rewiring per BOQ",
        "quantity": 1, "price_unit": 650000,
    })],
}))
if pr2:
    def _drive_pr2():
        pr2.action_confirm()
        pr2.action_accounts_check()
        pr2.action_ce_approve()
        pr2.action_send_pc()
        wiz = env["mcb.pr.rfq.wizard"].create({
            "request_id": pr2.id,
            "vendor_ids": [(6, 0, [vendor4.id, vendor5.id])],
        })
        wiz.action_generate()
        return pr2.procurement_method, pr2.noal_required
    run("PR2 drive to in_progress + RFQs", _drive_pr2)

    ta2 = run("PR2 technical analysis", lambda: env["mcb.technical.analysis"].create({
        "request_id": pr2.id, "ta_type": "ta2"}))
    if ta2:
        run("PR2 TA: fill vendors", ta2.action_fill_vendors)
        ta2.line_ids.write({"spec_compliance": True, "delivery_compliance": True, "result": "pass"})
        run("PR2 TA: done", ta2.action_done)

    cs2 = run("PR2 comparative statement", lambda: env["mcb.comparative.statement"].create({
        "request_id": pr2.id, "technical_analysis_id": ta2.id if ta2 else False,
        "circular_date": today - timedelta(days=25),
        "opening_date": today - timedelta(days=12),
        "pc_comment": "<p>BD Builders Ltd quoted the lowest price and has prior "
                      "satisfactory experience with MCB. Recommended for NOAL.</p>",
    }))
    if cs2:
        run("PR2 CS: fill vendors", cs2.action_fill_vendors)
        run("PR2 CS: done", cs2.action_done)

    eval2 = run("PR2 evaluation", lambda: env["mcb.vendor.evaluation"].create({
        "request_id": pr2.id, "cs_id": cs2.id if cs2 else False, "eval_type": "eval2"}))
    if eval2 and not eval2.line_ids:
        for v in cs2.vendor_line_ids.mapped("vendor_id"):
            env["mcb.vendor.evaluation.line"].create({
                "evaluation_id": eval2.id, "vendor_id": v.id,
                "price_score": 38 if v == vendor4 else 30,
                "quality_score": 28, "delivery_score": 14, "experience_score": 14,
            })
        eval2.recommended_vendor_id = vendor4.id
        run("PR2 evaluation: done", eval2.action_done)
        run("PR2 evaluation: create PO (+draft NOAL)", eval2.action_create_po)

    po2_final = env["purchase.order"].search([("mcb_pr_id", "=", pr2.id), ("state", "=", "draft")], limit=1)
    noal2 = po2_final.mcb_noal_id if po2_final else False
    if noal2:
        def _issue_noal2():
            noal2.contract_price = po2_final.amount_total
            noal2.action_issue()
            return noal2.state
        run("PR2 NOAL: issue", _issue_noal2)
        run("PR2 NOAL: acknowledge", noal2.action_acknowledge)

    if po2_final:
        def _confirm_po2():
            po2_final.action_mcb_check()
            po2_final.action_mcb_review()
            po2_final.action_mcb_approve()
            po2_final.button_confirm()
            return po2_final.state
        run("PR2 PO: 4-level approve + confirm (NOAL satisfied)", _confirm_po2)


# --- PR3: small Direct Purchase (<10,000) — demonstrates method threshold only
pr3 = run("create PR3 (Direct Purchase)", lambda: PR.create({
    "project_analytic_id": analytic_gbvie.id,
    "donor": "CARE",
    "delivery_point": "Head Office Store",
    "line_ids": [(0, 0, {
        "name": "Office stationery (A4 paper, pens, files)",
        "quantity": 1, "price_unit": 8000,
    })],
}))
if pr3:
    def _drive_pr3():
        pr3.action_confirm()
        pr3.action_accounts_check()
        pr3.action_ce_approve()
        return pr3.procurement_method, pr3.state
    run("PR3 drive to approved (Direct method)", _drive_pr3)


# =====================================================================
# PART C — ACCOUNTS
# =====================================================================
general_j.mcb_require_approval = True

jv1 = run("post JV (approval-gated)", lambda: (lambda mv: (
    mv.action_mcb_check(), mv.action_mcb_review(), mv.action_mcb_approve(),
    mv.action_post(), mv
)[-1])(env["account.move"].create({
    "move_type": "entry", "journal_id": general_j.id, "date": today,
    "ref": "Reclass — office supplies to project cost centre",
    "line_ids": [
        (0, 0, {"account_id": expense_acc.id, "name": "Office supplies reclass",
                "debit": 15000, "analytic_distribution": {str(analytic_gbvie.id): 100}}),
        (0, 0, {"account_id": liability_acc.id, "name": "Contra", "credit": 15000}),
    ],
})))

receipt1 = run("post receipt voucher (Bank)", lambda: (lambda mv: (mv.action_post(), mv)[-1])(
    env["account.move"].create({
        "move_type": "entry", "journal_id": bank_j.id, "date": today,
        "ref": "Donor contribution — CARE tranche 3",
        "line_ids": [
            (0, 0, {"account_id": bank_j.default_account_id.id,
                    "name": "CARE tranche 3", "debit": 500000}),
            (0, 0, {"account_id": income_acc.id, "name": "Donor contribution",
                    "credit": 500000, "analytic_distribution": {str(analytic_care.id): 100}}),
        ],
    })))

payment1 = run("post payment voucher (Bank)", lambda: (lambda mv: (mv.action_post(), mv)[-1])(
    env["account.move"].create({
        "move_type": "entry", "journal_id": bank_j.id, "date": today,
        "partner_id": vendor1.id if vendor1 else False,
        "ref": "Payment — Gemini Furniture invoice GF-2201",
        "line_ids": [
            (0, 0, {"account_id": expense_acc.id, "name": "Furniture purchase",
                    "debit": 90000, "analytic_distribution": {str(analytic_gbvie.id): 100}}),
            (0, 0, {"account_id": bank_j.default_account_id.id,
                    "name": "Payment to Gemini Furniture", "credit": 90000}),
        ],
    })))

checklist_pay = run("payment checklist (Annex-28)", lambda: env["mcb.payment.checklist"].create({
    "move_id": payment1.id, "project_name": "GBViE", "funded_by": "CARE",
}))
if checklist_pay:
    for l in checklist_pay.line_ids[:12]:
        l.status = "yes"
    run("payment checklist: done", checklist_pay.action_done)

# --- Wizards persisted as records for report/html preview
wiz_bank_recon = run("bank recon wizard record", lambda: env["mcb.bank.recon.wizard"].create({
    "journal_id": bank_j.id, "date_to": today, "statement_balance": 950000,
}))
wiz_cheque_reg = run("cheque register wizard record", lambda: env["mcb.cheque.register.wizard"].create({
    "journal_id": bank_j.id, "date_from": today - timedelta(days=30), "date_to": today,
    "project_name": "Head Office", "funded_by": "Multiple Donors",
}))
wiz_top_sheet = run("expenses top sheet wizard record", lambda: env["mcb.top.sheet.wizard"].create({
    "date_from": today - timedelta(days=30), "date_to": today,
    "analytic_account_id": analytic_gbvie.id,
    "project_name": "GBViE", "funded_by": "CARE",
}))
wiz_vat_tds = run("VAT/TDS wizard record", lambda: env["mcb.vat.tds.wizard"].create({
    "date_from": today - timedelta(days=30), "date_to": today,
}))
wiz_analytic = run("donor analytic report wizard record", lambda: env["mcb.analytic.report.wizard"].create({
    "analytic_account_ids": [(6, 0, [analytic_care.id, analytic_unfpa.id])],
    "date_from": today - timedelta(days=90), "date_to": today,
}))

# =====================================================================
# CASH ADVANCE / IOU / PETTY CASH
# =====================================================================
adv1 = run("create advance", lambda: env["mcb.advance"].create({
    "employee_id": emp_rashed.id, "activity_name": "Community awareness session — Camp 12",
    "project_analytic_id": analytic_gbvie.id, "funded_by": "CARE",
    "journal_id": bank_j.id,
    "line_ids": [
        (0, 0, {"name": "Venue and refreshment", "amount": 8000}),
        (0, 0, {"name": "Transport", "amount": 3000}),
        (0, 0, {"name": "Materials", "amount": 4000}),
    ],
}))
if adv1:
    def _drive_adv1():
        adv1.action_submit()
        adv1.action_finance_check()
        adv1.action_review()
        adv1.action_approve()
        adv1.action_pay()
        return adv1.state
    run("advance: drive to paid", _drive_adv1)

    adj1 = run("advance adjustment", lambda: env["mcb.advance.adjustment"].create({
        "advance_id": adv1.id,
        "line_ids": [
            (0, 0, {"name": "Venue and refreshment", "amount": 7500, "account_id": expense_acc.id}),
            (0, 0, {"name": "Transport", "amount": 3200, "account_id": expense_acc.id}),
            (0, 0, {"name": "Materials", "amount": 3800, "account_id": expense_acc.id}),
        ],
    }))
    if adj1:
        run("advance adjustment: submit + approve", lambda: (
            adj1.action_submit(), adj1.action_approve(), adj1.state)[-1])

iou1 = run("create IOU", lambda: env["mcb.iou"].create({
    "employee_id": emp_farzana.id, "purpose": "Urgent office stationery purchase",
    "amount": 2500, "project_analytic_id": analytic_gbvie.id, "funded_by": "CARE",
    "journal_id": bank_j.id,
}))
if iou1:
    def _drive_iou1():
        iou1.action_submit()
        iou1.action_approve()
        iou1.action_pay()
        return iou1.state
    run("IOU: drive to paid", _drive_iou1)
    run("IOU: adjust/settle", lambda: (
        setattr(iou1, "settle_account_id", expense_acc.id),
        setattr(iou1, "settle_amount_spent", 2350),
        iou1.action_adjust(), iou1.state)[-1])

# Petty Cash journal (none exists for co1) + top-up + book entries
petty_j = env["account.journal"].search([("type", "=", "cash"), ("company_id", "=", CO1)], limit=1)
if not petty_j:
    petty_j = run("create Petty Cash journal", lambda: env["account.journal"].create({
        "name": "Petty Cash", "type": "cash", "company_id": CO1, "code": "PCSH",
    }))
if petty_j:
    petty_j.mcb_petty_cash_limit = 20000

topup1 = run("petty cash top-up", lambda: env["mcb.petty.topup"].create({
    "cash_journal_id": petty_j.id, "bank_journal_id": bank_j.id, "amount": 15000,
}))
if topup1:
    def _drive_topup():
        topup1.action_request()
        topup1.action_approve()
        topup1.action_done()
        return topup1.state
    run("top-up: drive to done", _drive_topup)

# a couple of small petty-cash payments so the Book/Statement wizard has rows
if petty_j:
    def _petty_payment(desc, amount):
        mv = env["account.move"].create({
            "move_type": "entry", "journal_id": petty_j.id, "date": today,
            "ref": desc,
            "line_ids": [
                (0, 0, {"account_id": expense_acc.id, "name": desc, "debit": amount,
                        "analytic_distribution": {str(analytic_gbvie.id): 100}}),
                (0, 0, {"account_id": petty_j.default_account_id.id,
                        "name": desc, "credit": amount}),
            ],
        })
        mv.action_post()
        return mv
    run("petty payment 1 (courier)", lambda: _petty_payment("Courier charges", 450))
    run("petty payment 2 (tea/snacks)", lambda: _petty_payment("Office tea & snacks", 1200))

cash_count1 = run("cash count (Annex-14)", lambda: env["mcb.cash.count"].create({
    "journal_id": petty_j.id, "project_name": "Head Office", "funded_by": "Core",
}))
if cash_count1:
    denom_qty = {1000: 10, 500: 6, 200: 5, 100: 8, 50: 4, 20: 5, 10: 2, 5: 0, 2: 0, 1: 0}
    for l in cash_count1.line_ids:
        l.quantity = denom_qty.get(l.denomination, 0)
    run("cash count: approve", cash_count1.action_approve)

wiz_petty_book = run("petty book wizard record", lambda: env["mcb.petty.book.wizard"].create({
    "journal_id": petty_j.id, "date_from": today - timedelta(days=30), "date_to": today,
    "project_name": "Head Office", "funded_by": "Core",
}))

env.cr.commit()
print("=== BATCH 1 (Purchase + Accounts + Advances) DONE ===")
for name, status, err in RESULTS:
    if status == "FAIL":
        print("FAILED:", name, "->", err)
print(f"{sum(1 for _,s,_ in RESULTS if s=='OK')}/{len(RESULTS)} steps OK")
