from datetime import timedelta
from odoo import api, models, _, fields
from odoo.exceptions import ValidationError

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def action_confirm(self):
        res = super(SaleOrder, self).action_confirm()

        for line in self.order_line:
            if line.training_date and line.selected_employee:
                line_partner = None
                if line.selected_employee.user_id:
                    line_partner = line.selected_employee.user_partner_id
                else:
                    presumed_partner = self.env['res.partner'].search([('name', '=', line.selected_employee.name)], limit=1)
                    if len(presumed_partner) == 0:
                        line.selected_employee.user_partner_id = self.env['res.partner'].create({
                            'name': line.selected_employee.name,
                        })
                        line_partner = line.selected_employee.user_partner_id
                    else:
                        line_partner = presumed_partner

                raise ValueError(f"""THERE IS NO PARTNER !!!!!!!!!!!!!!
                employee.user_partner_id = {line.selected_employee.user_partner_id.name}
                employee.user_id = {line.selected_employee.user_id.name}
                employee.user_id.partner_id = {line.selected_employee.user_id.partner_id.name}
                line_partner = {line_partner.name}""")
                
                self.env['calendar.event'].create({
                    'name':'Training',
                    'start_date':line.training_date,
                    'stop_date':line.training_date + timedelta(hours=8),
                    'allday':True,
                    'partner_ids':[(4, line_partner.id)],
                })

        return res


