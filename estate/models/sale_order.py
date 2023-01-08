from datetime import timedelta
from odoo import api, models, _, fields
from odoo.exceptions import ValidationError

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def action_confirm(self):
        max_amount_approvable = self.get_user_max_amount(user=self.env.user)

        if max_amount_approvable >= self.amount_total:
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
                            line.selected_employee.user_partner_id = presumed_partner
                            line_partner = presumed_partner

                    self.env.user.partner_id.approved_orders += 1
                    
                    self.env['calendar.event'].create({
                        'name':'Training',
                        'start_date':line.training_date,
                        'stop_date':line.training_date + timedelta(hours=8),
                        'allday':True,
                        'recurrency':line.recurring,
                        'rrule':"FREQ=WEEKLY",
                        'partner_ids':[(4, line_partner.id)],
                    })
        else:
            self.message_post(body="You don't have the permissions to confirm this order, please contact a manager to get your quotation approved")
            return

        return super(SaleOrder, self).action_confirm()

    def ask_approval(self):
        manager = self.get_available_manager()
        if manager:
            for line in self.order_line:
                if line.training_date and line.selected_employee:
                    recurring_note = ""
                    if line.recurring:
                        recurring_note = "and the training is set to be recurring"
                    self.activity_schedule(
                        'Need approval for quotation',
                        date_deadline=line.training_date,
                        user_id=manager.id,
                        summary='Need approval for quotation, get a manager of high enough level to approve the quotation',
                        note=f'Total amount of the sale : {self.amount_total} {recurring_note}'
                    )
        else:
            self.message_post(body="No managers can currently fullfill this order, please get in contact with an administrator to get this fixed, or try deviding your order into multiple ones")

    def get_user_max_amount(self, user):
        if not user:
            user = self.env.user
        if user.partner_id.max_amount != 0:
            return user.partner_id.max_amount

        max = self.env['res.groups'].default_get(['max_amount'])['max_amount']

        for group in user.groups_id:
            if group.max_amount and group.max_amount > max:
                max = group.max_amount

        return max

    def get_available_manager(self):
        possible_managers = self.env['res.users'].browse([])
        users = self.env['res.users'].search([])

        for user in users:
            if user.partner_id.max_amount > self.amount_total or (user.partner_id.max_amount == 0 and self.get_user_max_amount(user=user) > self.amount_total):
                possible_managers = possible_managers.union(user)

        possible_managers = sorted(possible_managers, key=lambda m: m.partner_id.approved_orders)

        if len(possible_managers) > 0:
            return possible_managers[0]
        else:
            return False



