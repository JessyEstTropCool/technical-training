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
                    #path = "None"
                    if line.selected_employee.user_id:
                        line_partner = line.selected_employee.user_partner_id
                        #path = "has user"
                    else:
                        presumed_partner = self.env['res.partner'].search([('name', '=', line.selected_employee.name)], limit=1)
                        if len(presumed_partner) == 0:
                            line.selected_employee.user_partner_id = self.env['res.partner'].create({
                                'name': line.selected_employee.name,
                            })
                            line_partner = line.selected_employee.user_partner_id
                            #path = "new user"
                        else:
                            line.selected_employee.user_partner_id = presumed_partner
                            line_partner = presumed_partner
                            #path = "searched user"

                    # self.message_post(body=f"""This is where the partner comes from
                    #     \nemployee.user_partner_id = {line.selected_employee.user_partner_id.name}
                    #     \nemployee.user_id = {line.selected_employee.user_id.name}
                    #     \nemployee.user_id.partner_id = {line.selected_employee.user_id.partner_id.name}
                    #     \nline_partner = {line_partner.name}
                    #     \npath = {path}
                    #     \nmaxamount = {max_amount_approvable}""")
                    
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
            self.message_post(body="No managers can currently fullfill this order, please get in contact with an administrator to get this fixed")

    def get_user_max_amount(self, user):
        if not user:
            user = self.env.user
        if user.partner_id.max_amount != 0:
            #self.message_post(body=f"Max amount (user) = {user.partner_id.max_amount}")
            return user.partner_id.max_amount

        max = 500
        #cool_str = "The groups"

        for group in user.groups_id:
            # cool_str += "\n" + group.name + ", ma = "
            # if group.max_amount:
            #     cool_str += str(group.max_amount)

            if group.max_amount and group.max_amount > max:
                max = group.max_amount

        # self.message_post(body=f"""
        #     Max amount (groups) = {max},
        #     g:{cool_str}
        #     self: {self.name} {self}
        #     self.user_id: {self.user_id.name} {self.user_id}
        #     groups:{self.user_id.groups_id}""")

        return max

    def get_available_manager(self):
        possible_managers = self.env['res.users'].browse([])
        partners = self.env['res.users'].search([
            #'|',
            #('max_amount', '>', self.amount_total),
            ('partner_id.max_amount', '=', 0)
        ])

        cool = ""
        for partner in partners:
            cool += partner.name + " (" + partner.partner_id.name + ", " + str(partner.partner_id) + "), "
            if self.get_user_max_amount(user=partner) > self.amount_total:
                possible_managers.union(partner)

        cool += "\n"
        for partner in possible_managers:
            cool += partner.name + ", "

        raise TimeoutError(cool) #FIXME please idk what's happening

        if len(possible_managers) > 0:
            return possible_managers[0]
        else:
            return False



