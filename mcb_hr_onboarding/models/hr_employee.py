from datetime import timedelta

from odoo import api, fields, models


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    mcb_onboarding_plan_id = fields.Many2one(
        "mail.activity.plan", string="Onboarding Plan",
        domain="[('res_model','=','hr.employee')]", tracking=True,
    )
    mcb_onboarding_launched = fields.Boolean(string="Onboarding Launched",
        readonly=True, copy=False, tracking=True)
    mcb_onboarding_progress = fields.Float(
        string="Onboarding Progress (%)",
        compute="_compute_onboarding_progress",
    )

    @api.depends("activity_ids", "activity_ids.user_id", "mcb_onboarding_launched")
    def _compute_onboarding_progress(self):
        # We approximate progress as "% of activities created from the plan that
        # are already done" — done activities are removed from activity_ids, so
        # we compare to the launched plan's expected step count.
        for rec in self:
            if not rec.mcb_onboarding_launched or not rec.mcb_onboarding_plan_id:
                rec.mcb_onboarding_progress = 0.0
                continue
            total = max(len(rec.mcb_onboarding_plan_id.template_ids), 1)
            remaining = len(rec.activity_ids)
            done = max(0, total - remaining)
            rec.mcb_onboarding_progress = round((done / total) * 100.0, 1)

    def action_mcb_launch_onboarding(self):
        """Called by recruitment when an applicant becomes a hired employee."""
        plan = self.env.ref(
            "mcb_hr_onboarding.plan_mcb_employee_onboarding",
            raise_if_not_found=False,
        )
        if not plan:
            return
        for emp in self:
            if emp.mcb_onboarding_launched:
                continue
            emp.mcb_onboarding_plan_id = plan.id
            for tmpl in plan.template_ids:
                emp.activity_schedule(
                    activity_type_id=tmpl.activity_type_id.id,
                    summary=tmpl.summary or tmpl.activity_type_id.name,
                    note=tmpl.note or "",
                    user_id=(tmpl.responsible_id or emp.parent_id.user_id or emp.env.user).id,
                    date_deadline=fields.Date.context_today(emp) + timedelta(days=tmpl.delay_count or 0),
                )
            emp.mcb_onboarding_launched = True

    @api.model
    def _cron_mcb_probation_reminder(self):
        """ONB-004 — 15 days before probation_end schedule an activity on line manager."""
        today = fields.Date.context_today(self)
        target = today + timedelta(days=15)
        employees = self.search([
            ("mcb_probation_end_date", "=", target),
            ("active", "=", True),
        ])
        act_type = self.env.ref("mail.mail_activity_data_todo", raise_if_not_found=False)
        for emp in employees:
            user = emp.parent_id.user_id or self.env.ref("base.user_admin")
            emp.activity_schedule(
                activity_type_id=act_type.id if act_type else False,
                summary="Probation confirmation decision due",
                note="Please complete the probation review and confirm continuation, extension, or termination.",
                user_id=user.id,
                date_deadline=emp.mcb_probation_end_date,
            )
