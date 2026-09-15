from odoo import fields, models


class StockWarehouse(models.Model):
    """LOG-001 — the SOP's 'Warehouse information' main sheet.

    The SOP defines an MCB warehouse as 'a planned space managed by either its head
    office or together with its project office level'. These fields are that sheet.
    """
    _inherit = "stock.warehouse"

    mcb_is_mcb_store = fields.Boolean(
        string="MCB Store", default=False,
        help="Tick for warehouses that follow MCB's warehouse & inventory SOP.")
    mcb_office_type = fields.Selection([
        ("head", "Head Office"),
        ("project", "Project / Field Office"),
    ], string="Office Type", default="project")
    mcb_project_id = fields.Many2one("project.project", string="Project")
    mcb_donor = fields.Char(string="Funded By / Donor")
    mcb_storekeeper_id = fields.Many2one(
        "hr.employee", string="Store Keeper",
        help="SOP: the person responsible for adequate and safe storing conditions and "
             "for the accurate recording of all inventory movements.")
    mcb_focal_point_id = fields.Many2one(
        "hr.employee", string="Inventory Focal Point (Head Office)")
    mcb_address = fields.Char(string="Warehouse Address")
    mcb_storage_capacity = fields.Char(string="Storage Capacity")
    mcb_layout_plan = fields.Text(
        string="Layout & Storage Plan",
        help="SOP: shows, by Purchase Order, where items are currently stored and where "
             "arriving items can be stored. Keep it updated so free space is known.")
