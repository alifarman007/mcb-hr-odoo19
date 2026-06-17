from odoo import fields, models


class HrLeaveType(models.Model):
    _inherit = "hr.leave.type"

    mcb_block_during_probation = fields.Boolean(
        string="Block during probation (LVE-005)",
        default=False,
        help="If set, employees on probation cannot apply for this leave type.",
    )
    mcb_require_ce_approval = fields.Boolean(
        string="Require CE approval (3rd level)",
        default=False,
        help="SRS v2 feedback — in addition to Manager + HR, this leave type "
             "requires a final approval by a member of the MCB Chief Executive "
             "(CE) group. Used by Compensatory Leave (Manager + HR + CE).",
    )
