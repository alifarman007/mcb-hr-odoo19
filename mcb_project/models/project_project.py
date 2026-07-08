from odoo import api, fields, models, _
from odoo.exceptions import UserError


class ProjectProject(models.Model):
    _inherit = "project.project"

    # PRJ-001 profile
    mcb_project_code = fields.Char(string="Project Code", tracking=True)
    mcb_donor = fields.Char(string="Donor / Funder", tracking=True)
    mcb_contract_number = fields.Char(string="Contract Number")
    mcb_total_budget_bdt = fields.Monetary(string="Total Budget (BDT)",
                                           currency_field="currency_id")
    mcb_donor_currency_id = fields.Many2one("res.currency", string="Donor Currency")
    mcb_donor_budget = fields.Float(string="Budget (Donor Currency)")
    mcb_implementation_area = fields.Char(
        string="Implementation Area (camp/union/district)")
    mcb_activity_code = fields.Char(
        string="Activity Code (PRJ-003)",
        help="Aligned to the Chart of Accounts / Annexure-27 budget structure.")
    mcb_budget_id = fields.Many2one("budget.analytic", string="Project Budget (Annex-27)")

    # PRJ-007 close-out checklist
    mcb_closeout_final_report = fields.Boolean(string="Final report submitted")
    mcb_closeout_assets = fields.Boolean(string="Assets handed over")
    mcb_closeout_budget = fields.Boolean(string="Budget reconciled")
    mcb_closed_out = fields.Boolean(string="Closed Out", readonly=True, copy=False,
                                    tracking=True)

    mcb_assignment_ids = fields.One2many("mcb.project.assignment", "project_id")
    mcb_beneficiary_ids = fields.One2many("mcb.beneficiary.entry", "project_id")

    def action_mcb_closeout(self):
        for rec in self:
            missing = []
            if not rec.mcb_closeout_final_report:
                missing.append(_("final report"))
            if not rec.mcb_closeout_assets:
                missing.append(_("asset handover"))
            if not rec.mcb_closeout_budget:
                missing.append(_("budget reconciliation"))
            if missing:
                raise UserError(_(
                    "PRJ-007 — close-out checklist incomplete: %s.", ", ".join(missing)))
            rec.mcb_closed_out = True
            rec.active = False  # archive on close-out


class ProjectTask(models.Model):
    _inherit = "project.task"

    # MON-002 — % complete, shown in Gantt
    mcb_progress = fields.Integer(string="% Complete", default=0)
    mcb_task_level = fields.Selection([
        ("output", "Output"),
        ("activity", "Activity"),
        ("task", "Task"),
    ], default="task", string="Level (PRJ-002)")

    @api.constrains("mcb_progress")
    def _check_progress(self):
        for t in self:
            if not 0 <= t.mcb_progress <= 100:
                raise UserError(_("% Complete must be between 0 and 100."))


class ProjectMilestone(models.Model):
    _inherit = "project.milestone"

    @api.model
    def _cron_mcb_milestone_alert(self):
        """MON-003 — auto-alert the PM when a milestone slips past its deadline."""
        today = fields.Date.context_today(self)
        late = self.search([("is_reached", "=", False),
                            ("deadline", "!=", False),
                            ("deadline", "<", today)])
        for ms in late:
            user = ms.project_id.user_id
            if not user:
                continue
            already = self.env["mail.activity"].search_count([
                ("res_model", "=", "project.milestone"), ("res_id", "=", ms.id),
                ("user_id", "=", user.id)], limit=1)
            if not already:
                self.env["mail.activity"].create({
                    "res_model_id": self.env["ir.model"]._get_id("project.milestone"),
                    "res_id": ms.id,
                    "activity_type_id": self.env.ref("mail.mail_activity_data_todo").id,
                    "user_id": user.id,
                    "summary": _("Milestone '%s' is overdue (MON-003)", ms.name),
                    "note": _("Planned: %s — not yet reached.", ms.deadline),
                })
