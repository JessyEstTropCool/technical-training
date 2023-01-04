from odoo import fields, models

class ResGroups(models.Model):
    _inherit = 'res.groups'
    max_amount = fields.Float(string="Max approval amount", default=500) #max amount able to be approve by managers of this group
