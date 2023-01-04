from datetime import timedelta
from odoo import api, models, _, fields
from odoo.exceptions import ValidationError

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def action_confirm(self):
        max_amount_approvable = self.env.user.partner_id.get_user_max_amount()

        if max_amount_approvable >= self.amount_total:
            for line in self.order_line:
                if line.training_date and line.selected_employee:
                    line_partner = None
                    path = "None"
                    if line.selected_employee.user_id:
                        line_partner = line.selected_employee.user_partner_id
                        path = "has user"
                    else:
                        presumed_partner = self.env['res.partner'].search([('name', '=', line.selected_employee.name)], limit=1)
                        if len(presumed_partner) == 0:
                            line.selected_employee.user_partner_id = self.env['res.partner'].create({
                                'name': line.selected_employee.name,
                            })
                            line_partner = line.selected_employee.user_partner_id
                            path = "new user"
                        else:
                            line.selected_employee.user_partner_id = presumed_partner
                            line_partner = presumed_partner
                            path = "searched user"

                    self.message_post(body=f"""This is where the partner comes from
                        \nemployee.user_partner_id = {line.selected_employee.user_partner_id.name}
                        \nemployee.user_id = {line.selected_employee.user_id.name}
                        \nemployee.user_id.partner_id = {line.selected_employee.user_id.partner_id.name}
                        \nline_partner = {line_partner.name}
                        \npath = {path}
                        \nmaxamount = {max_amount_approvable}""")
                    
                    self.env['calendar.event'].create({
                        'name':'Training',
                        'start_date':line.training_date,
                        'stop_date':line.training_date + timedelta(hours=8),
                        'allday':True,
                        'partner_ids':[(4, line_partner.id)],
                    })
        else:
            self.message_post(body="No, bad user, don't do that")
            return

        return super(SaleOrder, self).action_confirm()



