from odoo import fields, models


class McbQuarterlyReportWizard(models.TransientModel):
    """MON-004 — quarterly project report: planned vs completed activities,
    % achievement, beneficiary reach, challenges & next-quarter plan."""
    _name = "mcb.quarterly.report.wizard"
    _inherit = ["mcb.xlsx.mixin"]
    _description = "Quarterly Project Report (MON-004)"

    project_id = fields.Many2one("project.project", required=True)
    date_from = fields.Date(required=True)
    date_to = fields.Date(required=True, default=fields.Date.context_today)
    challenges = fields.Text(string="Key Challenges")
    next_plan = fields.Text(string="Next Quarter Plan")

    def _stats(self):
        tasks_planned = self.env["project.task"].search([
            ("project_id", "=", self.project_id.id),
            ("date_deadline", ">=", self.date_from),
            ("date_deadline", "<=", self.date_to)])
        tasks_done = tasks_planned.filtered(lambda t: t.state == "1_done")
        bens = self.env["mcb.beneficiary.entry"].search([
            ("project_id", "=", self.project_id.id),
            ("date", ">=", self.date_from), ("date", "<=", self.date_to)])
        return {
            "planned": tasks_planned,
            "done": tasks_done,
            "pct": (len(tasks_done) / len(tasks_planned) * 100.0) if tasks_planned else 0.0,
            "ben_direct": sum(bens.filtered(
                lambda b: b.beneficiary_type == "direct").mapped("total")),
            "ben_indirect": sum(bens.filtered(
                lambda b: b.beneficiary_type == "indirect").mapped("total")),
            "ben_male": sum(bens.mapped("male")),
            "ben_female": sum(bens.mapped("female")),
            "milestones": self.env["project.milestone"].search([
                ("project_id", "=", self.project_id.id)]),
        }

    def action_print_pdf(self):
        return self.env.ref("mcb_project.action_report_mcb_quarterly").report_action(self)
