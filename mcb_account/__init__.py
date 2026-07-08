from . import models
from . import wizard


def post_init_hook(env):
    """Configure Bangladesh NGO finance defaults.

    Review-hardened (plan findings 1/4/10/20/25):
    - July–June fiscal year + GBP/AUD activation for every company (PER-005, COA-005)
    - Restrictive audit trail (VOU-010 / PER-003)
    - TDS *withholding-on-payment* taxes (l10n_account_withholding_tax) only for
      Bangladesh-flavoured companies with an installed chart (TAX-001)
    - Employee Advance + Fund Balance accounts per chart company
    """
    for cur_code in ("GBP", "AUD", "USD", "BDT"):
        cur = env["res.currency"].with_context(active_test=False).search(
            [("name", "=", cur_code)], limit=1)
        if cur and not cur.active:
            cur.active = True

    for company in env["res.company"].search([]):
        vals = {"fiscalyear_last_day": 30, "fiscalyear_last_month": "6"}
        if "restrictive_audit_trail" in company._fields:
            vals["restrictive_audit_trail"] = True
        company.write(vals)

        chart_installed = env["account.account"].sudo().search_count(
            [("company_ids", "in", company.id)], limit=1
        )
        if not chart_installed:
            continue
        _ensure_core_accounts(env, company)
        is_bd = (company.country_id and company.country_id.code == "BD") or \
                company.currency_id.name == "BDT"
        if is_bd:
            _ensure_tds_taxes(env, company)


def _ensure_core_accounts(env, company):
    Account = env["account.account"].sudo().with_company(company)

    def get_or_create(code, name, account_type):
        acc = Account.search(
            [("code", "=", code), ("company_ids", "in", company.id)], limit=1
        )
        if not acc:
            acc = Account.create({"code": code, "name": name, "account_type": account_type})
        return acc

    get_or_create("102910", "Employee Advances", "asset_current")
    get_or_create("300190", "Fund Balance (NGO)", "equity")
    get_or_create("200910", "TDS Payable (Withholding)", "liability_current")


def _ensure_tds_taxes(env, company):
    Account = env["account.account"].sudo().with_company(company)
    Tax = env["account.tax"].sudo().with_company(company)
    tds_payable = Account.search(
        [("code", "=", "200910"), ("company_ids", "in", company.id)], limit=1)
    tds_group = env["account.tax.group"].sudo().search(
        [("name", "=", "TDS"), ("country_id.code", "=", "BD")], limit=1)
    if not tds_group:
        tds_group = env["account.tax.group"].sudo().create({
            "name": "TDS", "country_id": env.ref("base.bd").id,
        })
    withholding_supported = "is_withholding_tax_on_payment" in Tax._fields
    for rate in (2.0, 3.0, 5.0, 7.5, 10.0):
        name = f"TDS {rate:g}%"
        if Tax.search([("name", "=", name), ("company_id", "=", company.id)], limit=1):
            continue
        vals = {
            "name": name,
            "amount_type": "percent",
            "amount": -rate,
            "type_tax_use": "purchase",
            "tax_group_id": tds_group.id,
            "country_id": env.ref("base.bd").id,
            "company_id": company.id,
            "invoice_repartition_line_ids": [
                (0, 0, {"repartition_type": "base"}),
                (0, 0, {"repartition_type": "tax", "account_id": tds_payable.id}),
            ],
            "refund_repartition_line_ids": [
                (0, 0, {"repartition_type": "base"}),
                (0, 0, {"repartition_type": "tax", "account_id": tds_payable.id}),
            ],
        }
        if withholding_supported:
            vals["is_withholding_tax_on_payment"] = True
        Tax.create(vals)
