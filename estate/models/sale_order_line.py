from odoo import fields, models, Command

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'
    training_date = fields.Date(string="Training Date")
    selected_employee = fields.Many2one(comodel_name="hr.employee", string="Selected Employee", ondelete="set null")
