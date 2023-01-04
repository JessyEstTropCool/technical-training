from odoo import fields, models

class ResPartner(models.Model):
    _inherit = 'res.partner'
    max_amount = fields.Float(string="Max approval amount") #max amount able to be approve by managers of this group

    def get_user_max_amount(self):
        if self.max_amount != 0:
            self.message_post(body="Max amount (user) = " + self.max_amount)
            return self.max_amount

        max = 500

        for group in self.user_id.groups_id:
            if group.max_amount and group.max_amount > max:
                max = group.max_amount

        self.message_post(body=f"Max amount (groups) = {max}")

        return max
