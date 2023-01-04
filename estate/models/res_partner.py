from odoo import fields, models

class ResPartner(models.Model):
    _inherit = 'res.partner'
    max_amount = fields.Float(string="Max approval amount") #max amount able to be approve by managers of this group

    def get_user_max_amount(self):
        if self.max_amount != 0:
            #self.message_post(body="Max amount (user) = " + self.max_amount)
            raise TimeoutError(f"Max amount (user) = {max}")

            return self.max_amount

        max = 500
        cool_str = "The groups"

        for group in self.user_id.groups_id.mapped('name'):
            raise TimeoutError(group)
            cool_str += "\n" + group.name + ", ma = "
            if group.max_amount and group.max_amount > max:
                max = group.max_amount
                cool_str += str(group.max_amount)

        #self.message_post(body=f"Max amount (groups) = {max}")
        raise TimeoutError(f"""
            Max amount (groups) = {max},
            g:{cool_str}
            self: {self.name} {self}
            self.user_id: {self.user_id.name} {self.user_id}
            groups:{self.groups_id}"""
        )

        return max
