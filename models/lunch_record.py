from odoo import models, fields, api, exceptions, _


class LunchRecord(models.Model):
    _name = 'lunch.record'
    _description = 'Employee Lunch Record'
    _order = 'date desc'

    employee_id = fields.Many2one(
        'hr.employee', string='Employee',
        required=True, readonly=True,
        default=lambda self: self._default_employee()
    )
    date = fields.Date(
        string='Date',
        default=fields.Date.context_today,
        required=True
    )
    lunch_type = fields.Many2one(
        'lunch.types', string='Lunch Type', required=True
    )
    # cost = fields.Float(
    #     string='Cost', related='lunch_types.cost', readonly=True
    # )

    _sql_constraints = [
        ('unique_employee_date',
         'unique(employee_id, date)',
         'Lunch already recorded for this employee on this date!')
    ]


    # ---------- default employee ----------
    def _default_employee(self):
        """Return the hr.employee linked to the current user."""
        return self.env['hr.employee'].search([
            ('user_id', '=', self.env.user.id)
        ], limit=1)

    # ---------- create ----------
    @api.model_create_multi
    @api.model
    def create(self, vals_list):
        """Force employee_id to logged-in user's employee (for non-admins)."""
        for vals in vals_list:
            if not self.env.user.has_group('lunch_management.group_lunch_admin'):
                employee = self.env['hr.employee'].search([
                    ('user_id', '=', self.env.user.id)
                ], limit=1)
                if not employee:
                    raise exceptions.ValidationError(
                        _("No employee linked with your user account.")
                    )
                vals['employee_id'] = employee.id
        return super(LunchRecord, self).create(vals_list)

    # ---------- security ----------
    def _check_employee_access(self):
        for rec in self:
            if self.env.user.has_group('base.group_hr_manager'):
                continue
            emp = self.env['hr.employee'].search([
                ('user_id', '=', self.env.user.id)
            ], limit=1)
            if rec.employee_id != emp:
                raise exceptions.AccessError(
                    _("You cannot modify other employees' lunch records.")
                )

    def write(self, vals):
        self._check_employee_access()
        return super(LunchRecord, self).write(vals)

    def unlink(self):
        self._check_employee_access()
        return super(LunchRecord, self).unlink()


