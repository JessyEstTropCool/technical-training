from datetime import timedelta
from odoo import api, models, _, fields
from odoo.exceptions import ValidationError

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def action_confirm(self):
        res = super(SaleOrder, self).action_confirm()
        partner = self.partner_id

        for line in self.order_line:
            if line.training_date and line.selected_employee:
                if line.selected_employee.partner_id:
                    self.env['calendar.event'].create({
                        'name':'Training',
                        'start_date':line.training_date,
                        'stop_date':line.training_date + timedelta(hours=8),
                        'allday':True,
                        'partner_ids':[(4, partner.id), (4, line.selected_employee.partner_id.id)],
                    })
                else:
                    raise ValueError(f"""THERE IS NO PARTNER !!!!!!!!!!!!!!
                    \nemployee.user_partner_id = {line.selected_employee.user_partner_id}
                    \nemployee.user_id = {line.selected_employee.user_id}
                    \nemployee.partner_id = {line.selected_employee.partner_id}
                    \nemployee.user_id.partner_id = {line.selected_employee.user_id.partner_id}""")

        return res


