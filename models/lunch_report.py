from odoo import models, fields, api
from datetime import datetime
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError


class LunchReportWizard(models.TransientModel):
    _name = 'lunch.report.wizard'
    _description = 'Lunch Report Wizard'

    date_from = fields.Date(string='From Date', required=True,
                            default=lambda self: fields.Date.today().replace(day=1))
    date_to = fields.Date(string='To Date', required=True,
                            default=fields.Date.today())

    report_type = fields.Selection([
        ('all', 'All Employees'),
        ('specific', 'Specific Employee')
    ], string="Report For", default='all', required=True)

    employee_id = fields.Many2one('hr.employee', string='Employee')

    @api.onchange('date_from')
    def _onchange_date_from(self):
        if self.date_from:
            dt = datetime.strptime(str(self.date_from), '%Y-%m-%d')
            self.date_to = (dt + relativedelta(months=1, days=-1)).date()

    def action_view_report(self):
        """Admin sees ONLY CONFIRMED | Employees see their own (draft + confirmed)"""
        self.ensure_one()

        domain = [('date', '>=', self.date_from), ('date', '<=', self.date_to)]

        # Admin → ONLY CONFIRMED records
        if self.env.user.has_group('base.group_system'):
            domain += [('state', '=', 'confirmed')]
        # Normal employee → only their own records (draft + confirmed)
        else:
            domain += [('employee_id.user_id', '=', self.env.uid)]

        if self.report_type == 'specific':
            if not self.employee_id:
                raise UserError("Please select an employee.")
            domain += [('employee_id', '=', self.employee_id.id)]

        # Use beautiful report list view if exists
        try:
            list_view = self.env.ref('19_lunch_management.view_lunch_record_report_list').id
        except:
            list_view = False

        action = {
            'name': 'Lunch Report',
            'type': 'ir.actions.act_window',
            'res_model': 'lunch.record',
            'view_mode': 'list,form',
            'views': [(list_view, 'list'), (False, 'form')],
            'domain': domain,
            'context': {
                'create': False,
                'edit': False,
                'delete': False,
            },
        }

        if self.report_type == 'all' and self.env.user.has_group('base.group_system'):
            action['context'] = {**action['context'], 'group_by': 'employee_id'}

        return action


    def action_print_report(self):
        """PDF: Same logic as View Report → Admin sees only confirmed"""
        self.ensure_one()

        domain = [('date', '>=', self.date_from), ('date', '<=', self.date_to)]

        # Admin → ONLY CONFIRMED
        if self.env.user.has_group('base.group_system'):
            domain += [('state', '=', 'confirmed')]
        # Normal employee → only their own
        else:
            domain += [('employee_id.user_id', '=', self.env.uid)]

        selected_emp_id = False
        if self.report_type == 'specific':
            if not self.employee_id:
                raise UserError("Please select an employee.")
            domain += [('employee_id', '=', self.employee_id.id)]
            selected_emp_id = self.employee_id.id

        records = self.env['lunch.record'].search(domain)
        if not records:
            raise UserError("No records found for the selected period.")

        report_data = {
            'date_from': self.date_from,
            'date_to': self.date_to,
            'employee_id': selected_emp_id,
            'is_admin': self.env.user.has_group('base.group_system'),
        }

        return self.env.ref('19_lunch_management.action_report_lunch').with_context(
            report_data=report_data
        ).report_action(records)