from odoo import fields, models

class ResPartner(models.Model):
    _inherit = 'res.partner'
    max_amount = fields.Float(string="Max approval amount") #max amount able to be approve by managers of this group

    def get_user_max_amount(self):
        return self.max_amount