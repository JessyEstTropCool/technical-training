from datetime import timedelta
from odoo import api, models, _, fields
from odoo.exceptions import ValidationError

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def action_confirm(self):
        res = super(SaleOrder, self).action_confirm()

        for line in self.order_line:
            if line.training_date and line.selected_employee:
                #raise TimeoutError(line.selected_employee.user_partner_id)
                self.env['calendar.event'].create({
                    'name':'Training',
                    'start_date':line.training_date,
                    'stop_date':line.training_date + timedelta(hours=8),
                    'allday':True,
                    'partner_ids':[(4, line.selected_employee.user_partner_id())],
                })
                

        return res


