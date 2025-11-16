from odoo import models, fields, api, exceptions, _
from datetime import datetime
import pytz


class LunchRecord(models.Model):
    _name = 'lunch.record'
    _description = 'Employee Lunch Record'
    _order = 'date desc'

    # NEW: State Field
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
    ], string='Status', default='draft', readonly=True, copy=False)

    # Confirm Button Visibility (Client-side)
    is_confirm_allowed = fields.Boolean(
        string="Confirm Allowed",
        compute='_compute_confirm_allowed',
        store=False
    )

    employee_id = fields.Many2one(
        'hr.employee', string='Employee',
        required=True,
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
    cost = fields.Float(
        string='Cost', related='lunch_type.cost', readonly=True, store=True
    )
    note = fields.Text(string='Remarks')

    day = fields.Char(
        string='Day',
        compute='_compute_day',
        store=True,
        readonly=True
    )

    _sql_constraints = [
        ('unique_employee_date',
         'unique(employee_id, date, state)',
         'Lunch already recorded for this employee on this date!')
    ]

    @api.constrains('employee_id', 'date')
    def _check_unique_lunch_per_day(self):
        for record in self:
            if record.date and record.state != 'cancelled':
                duplicate = self.env['lunch.record'].search([
                    ('employee_id', '=', record.employee_id.id),
                    ('date', '=', record.date),
                    ('id', '!=', record.id),
                    ('state', '!=', 'cancelled')
                ], limit=1)
                if duplicate:
                    raise exceptions.ValidationError(
                        f"Lunch record already exists for {record.employee_id.name} on {record.date.strftime('%B %d, %Y')} ({record.day}). "
                        "Only one record per day is allowed."
                    )

    def _default_employee(self):
        return self.env['hr.employee'].search([
            ('user_id', '=', self.env.user.id)
        ], limit=1)

    @api.depends('date')
    def _compute_day(self):
        for record in self:
            if record.date:
                record.day = record.date.strftime('%A')
            else:
                record.day = ''

    @api.model_create_multi
    def create(self, vals_list):
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
        records = super(LunchRecord, self).create(vals_list)
        # Set state to draft on create (for non-admin)
        if not self.env.user.has_group('base.group_system'):
            records.filtered(lambda r: r.state == 'draft').write({'state': 'draft'})
        return records

    def _check_employee_access(self):
        for rec in self:
            if self.env.user.has_group('base.group_system') or self.env.user.has_group('lunch_management.group_lunch_admin'):
                continue
            emp = self.env['hr.employee'].search([
                ('user_id', '=', self.env.user.id)
            ], limit=1)
            if rec.employee_id != emp:
                raise exceptions.AccessError(
                    _("You cannot modify other employees' lunch records.")
                )

    # BLOCK EDIT AFTER CONFIRM
    def write(self, vals):
        if 'state' not in vals:
            confirmed_records = self.filtered(lambda r: r.state == 'confirmed')
            if confirmed_records:
                raise exceptions.UserError(
                    _("You cannot edit a confirmed lunch record.")
                )
        self._check_employee_access()
        return super(LunchRecord, self).write(vals)

    # BLOCK DELETE FOR NON-ADMIN
    def unlink(self):
        if not self.env.user.has_group('base.group_system'):
            raise exceptions.AccessError(
                _("You are not allowed to delete lunch records. Contact Admin.")
            )
        return super(LunchRecord, self).unlink()

    # COMPUTE: Confirm Button Visibility
    @api.depends('state')
    def _compute_confirm_allowed(self):
        nepal_tz = pytz.timezone('Asia/Kathmandu')
        now = datetime.now(nepal_tz)
        current_time = now.time()
        start_pm = datetime.strptime("17:00", "%H:%M").time()  # 5 PM
        end_am = datetime.strptime("09:00", "%H:%M").time()    # 9 AM

        for rec in self:
            if rec.state != 'draft':
                rec.is_confirm_allowed = False
            else:
                rec.is_confirm_allowed = (start_pm <= current_time or current_time <= end_am)

    # STATE BUTTONS
    def action_confirm(self):
        for rec in self:
            if rec.state != 'draft':
                raise exceptions.UserError(_("Only draft records can be confirmed."))

            # Nepal Time Check
            nepal_tz = pytz.timezone('Asia/Kathmandu')
            now = datetime.now(nepal_tz)
            current_time = now.time()
            start_pm = datetime.strptime("17:00", "%H:%M").time()
            end_am = datetime.strptime("09:00", "%H:%M").time()

            if not (start_pm <= current_time or current_time <= end_am):
                raise exceptions.UserError(
                    _("You can only confirm lunch entries between 5:00 PM and 9:00 AM Nepal Time.")
                )

        self.write({'state': 'confirmed'})

    def action_cancel(self):
        for rec in self:
            if rec.state not in ('draft', 'confirmed'):
                raise exceptions.UserError(_("Only draft or confirmed records can be cancelled."))
        self.write({'state': 'cancelled'})

    def action_reset_draft(self):
        if not self.env.user.has_group('base.group_system'):
            raise exceptions.AccessError(_("Only Admin can reset to draft."))
        self.write({'state': 'draft'})

    @api.model
    def action_open_lunch_records_all(self):
        """Open All Lunch Records with 'Today' filter for Admin only"""
        action = self.env.ref('19_lunch_management.action_lunch_record_all').read()[0]
        context = {}
        if self.env.user.has_group('base.group_system'):
            context['search_default_filter_today'] = 1
        action['context'] = context
        return action