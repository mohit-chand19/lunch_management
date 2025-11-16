from odoo import models, fields, api
from datetime import datetime
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError
from odoo import _


class LunchReportWizard(models.TransientModel):
    _name = 'lunch.report.wizard'
    _description = 'Lunch Report Wizard'

    date_from = fields.Date(string='From Date', required=True, default=lambda self: fields.Date.today().replace(day=1))
    date_to = fields.Date(string='To Date', required=True, default=fields.Date.today())
    employee_id = fields.Many2one('hr.employee', string='Employee', default=lambda self: self._default_employee())

    def _default_employee(self):
        return self.env['hr.employee'].search([('user_id', '=', self.env.user.id)], limit=1)

    @api.onchange('date_from')
    def _onchange_date_from(self):
        if self.date_from:
            self.date_to = (datetime.strptime(str(self.date_from), '%Y-%m-%d') + relativedelta(months=1) - relativedelta(days=1)).date()

    def action_print_report(self):
        self.ensure_one()
        
        domain = [
            ('date', '>=', self.date_from),
            ('date', '<=', self.date_to),
        ]
        if not self.env.user.has_group('base.group_system'):
            domain += [('employee_id', '=', self.employee_id.id)]

        records = self.env['lunch.record'].search(domain)
        if not records:
            raise UserError(_("No lunch records found for the selected period."))

        report_data = {
            'date_from': self.date_from,
            'date_to': self.date_to,
            'employee_id': self.employee_id.id if not self.env.user.has_group('base.group_system') else False,
            'is_admin': self.env.user.has_group('base.group_system'),
            'company': self.env.company.read(['name', 'street', 'phone', 'email'])[0]
        }

        report = self.env.ref('19_lunch_management.action_report_lunch')
        return report.with_context(report_data=report_data).report_action(records)