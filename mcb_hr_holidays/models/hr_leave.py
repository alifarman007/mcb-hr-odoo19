from odoo import api, fields, models
from odoo.exceptions import ValidationError, UserError


class HrLeave(models.Model):
    _inherit = "hr.leave"

    # SRS v2 feedback — 3rd-level CE approval (Manager + HR + CE) for leave
    # types flagged on hr.leave.type (e.g. Compensatory Leave).
    mcb_require_ce_approval = fields.Boolean(
        related="holiday_status_id.mcb_require_ce_approval",
        string="Requires CE Approval", store=True, readonly=True,
    )
    mcb_ce_approved = fields.Boolean(string="CE Approved", copy=False, tracking=True, readonly=True)
    mcb_ce_approver_id = fields.Many2one("res.users", string="CE Approver", copy=False, readonly=True)

    def action_mcb_ce_approve(self):
        """3rd-level approval — only members of the MCB CE group may approve."""
        if not self.env.user.has_group("mcb_hr_employee.group_mcb_ce"):
            raise UserError(
                "Only members of the MCB Chief Executive (CE) group can give "
                "this third-level approval. Please ask the CE to log in and approve."
            )
        for leave in self:
            leave.mcb_ce_approved = True
            leave.mcb_ce_approver_id = self.env.user
            leave.message_post(
                body=f"<strong>CE approval granted</strong> by {self.env.user.name} "
                     f"(3rd-level approval for '{leave.holiday_status_id.name}')."
            )
        return True

    def _action_validate(self, check_state=True):
        # Block the final approval until a CE-group member has approved, for
        # leave types that require it (Manager + HR + CE).
        for leave in self:
            if leave.mcb_require_ce_approval and not leave.mcb_ce_approved:
                raise UserError(
                    f"'{leave.holiday_status_id.name}' requires a third-level CE "
                    f"approval before it can be finalised. A member of the MCB CE "
                    f"group must click 'CE Approve' first (Manager + HR + CE)."
                )
        return super()._action_validate(check_state=check_state)

    @api.constrains("employee_id", "holiday_status_id", "date_from")
    def _check_mcb_probation_block(self):
        """LVE-005 — Block restricted leave types while the employee is in probation."""
        for leave in self:
            emp = leave.employee_id
            ltype = leave.holiday_status_id
            if not emp or not ltype or not ltype.mcb_block_during_probation:
                continue
            req_date = fields.Date.to_date(leave.date_from) if leave.date_from else fields.Date.context_today(self)
            start = emp.mcb_probation_start_date
            end = emp.mcb_probation_end_date
            if start and end and start <= req_date <= end:
                raise ValidationError(
                    f"LVE-005 — {emp.name} is currently on probation "
                    f"({start.isoformat()} → {end.isoformat()}). "
                    f"The '{ltype.name}' leave type cannot be applied for "
                    f"during the probation period."
                )
