from odoo import models, fields, api, exceptions, _
from datetime import datetime, timedelta
import pytz


class LunchRecord(models.Model):
    _name = 'lunch.record'
    _description = 'Employee Lunch Record'
    _order = 'date desc'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _no_card = True

    # State Field
    state = fields.Selection([
        ('draft', 'Draft'),
        ('requested', 'Requested'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
    ], string='Status', default='draft', readonly=True, copy=False, tracking=True)
    
    name = fields.Char(
        string='Reference',
        compute='_compute_name',
        store=True,
        readonly=True
    )

    employee_id = fields.Many2one(
        'hr.employee', string='Employee',
        required=True,
        default=lambda self: self._default_employee()
    )
    
    # Computed field to determine if employee field should be readonly
    is_employee_readonly = fields.Boolean(
        string='Employee Readonly',
        compute='_compute_is_employee_readonly',
        store=False
    )
    
    date = fields.Date(
        string='Date',
        default=lambda self: self._default_lunch_date(),
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
    
    # New field for admin request
    is_admin_request = fields.Boolean(
        string='Admin Request',
        default=False,
        help='Record created by admin on behalf of employee'
    )
    
    # Computed field to check if user is admin
    is_user_admin = fields.Boolean(
        string='Is User Admin',
        compute='_compute_is_user_admin',
        store=False
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

    def _compute_is_user_admin(self):
        """Check if current user is admin"""
        for record in self:
            record.is_user_admin = self.env.user.has_group('base.group_system')
    
    def _compute_is_employee_readonly(self):
        """Employee field is readonly for non-admin users"""
        for record in self:
            record.is_employee_readonly = not self.env.user.has_group('base.group_system')

    def _default_lunch_date(self):
        """Return next working day (tomorrow, skip Saturday)"""
        nepal_tz = pytz.timezone('Asia/Kathmandu')
        today = datetime.now(nepal_tz).date()
        tomorrow = today + timedelta(days=1)
        
        # If tomorrow is Saturday (5), skip to Sunday (6)
        if tomorrow.weekday() == 5:
            tomorrow = tomorrow + timedelta(days=1)
        
        return tomorrow

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
            # Set employee automatically for non-admin
            if not self.env.user.has_group('lunch_management.group_lunch_admin'):
                employee = self.env['hr.employee'].search([('user_id', '=', self.env.user.id)], limit=1)
                if not employee:
                    raise exceptions.ValidationError(_("No employee linked with your user account."))
                vals['employee_id'] = employee.id

            # === AUTO SELECT LUNCH TYPE BASED ON DAY ===
            date_str = vals.get('date') or self._default_lunch_date()
            date_obj = fields.Date.from_string(date_str)
            weekday = date_obj.weekday()  # 0=Monday, 5=Saturday, 6=Sunday

            # Saturday = Holiday → Block creation (unless admin)
            if weekday == 5 and not self.env.user.has_group('base.group_system'):
                raise exceptions.ValidationError(
                    _("Saturday is a holiday. No lunch record allowed.")
                )

            # Determine lunch type
            lunch_type_name = "Non-Veg" if weekday in (0, 4) else "Veg"  # 0=Monday, 4=Friday

            lunch_type = self.env['lunch.types'].search([('lunch_type', '=', lunch_type_name)], limit=1)
            if not lunch_type:
                raise exceptions.ValidationError(
                    _(f"Lunch type '{lunch_type_name}' not found. Please create it in Configuration.")
                )
            vals['lunch_type'] = lunch_type.id

        # Create the records
        records = super(LunchRecord, self).create(vals_list)

        # Set state to draft
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
        # Block employee change for non-admin users
        if 'employee_id' in vals and not self.env.user.has_group('base.group_system'):
            raise exceptions.UserError(
                _("You cannot change the employee. Please contact admin if needed.")
            )
        
        # Block date change for non-admin users
        if 'date' in vals and not self.env.user.has_group('base.group_system'):
            raise exceptions.UserError(
                _("You cannot change the lunch date. The date is automatically set to tomorrow. Please contact admin if you need to change it.")
            )
        
        if 'state' not in vals:
            confirmed_records = self.filtered(lambda r: r.state in ('confirmed', 'requested'))
            if confirmed_records and not self.env.user.has_group('base.group_system'):
                raise exceptions.UserError(
                    _("You cannot edit a confirmed or requested lunch record.")
                )
        self._check_employee_access()
        return super(LunchRecord, self).write(vals)

    # Confirm Action with Validation Message
    def action_confirm(self):
        self.ensure_one()
        
        # Only admin can confirm requested records
        if self.state == 'requested' and not self.env.user.has_group('base.group_system'):
            raise exceptions.UserError(_("Only admin can confirm requested records. Please wait for admin approval."))
        
        if self.state not in ('draft', 'requested'):
            raise exceptions.UserError(_("Only draft or requested records can be confirmed."))

        nepal_tz = pytz.timezone('Asia/Kathmandu')
        now = datetime.now(nepal_tz)
        current_hour = now.hour + (now.minute / 60.0)

        timing = self.env['lunch.timing'].search([], limit=1)
        if not timing:
            raise exceptions.UserError(_("Lunch timing is not configured. Please contact admin."))

        # Check if within allowed time window (skip check for admin or requested records)
        if self.state != 'requested' and not self.env.user.has_group('base.group_system'):
            if not (timing.start_time <= current_hour <= timing.end_time):
                raise exceptions.UserError(
                    _("You cannot confirm lunch now. Confirmation is only allowed between %s and %s. Current time: %s") %
                    (self._format_time(timing.start_time), 
                    self._format_time(timing.end_time),
                    self._format_time(current_hour))
                )

        self.write({'state': 'confirmed'})
        
        # Add message if admin confirmed a requested record
        if self.state == 'confirmed' and self.env.user.has_group('base.group_system'):
            self.message_post(
                body=_('Admin %s confirmed this lunch record.') % self.env.user.name,
                message_type='notification',
                subtype_xmlid='mail.mt_note'
            )
        
        # Return action to reload the form and show notification
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Success!',
                'message': 'Lunch record has been confirmed.',
                'type': 'success',
                'sticky': False,
                'next': {
                    'type': 'ir.actions.act_window_close',
                }
            }
        }
    
    def _format_time(self, float_time):
        hours = int(float_time)
        minutes = int((float_time - hours) * 60)
        return f"{hours:02d}:{minutes:02d}"

    def action_cancel(self):
        """Allow cancellation only from draft state for employees"""
        for rec in self:
            if rec.state == 'cancelled':
                raise exceptions.UserError(_("This record is already cancelled."))
            
            # Only admin can cancel confirmed/requested records
            if rec.state in ('confirmed', 'requested') and not self.env.user.has_group('base.group_system'):
                raise exceptions.UserError(_("You cannot cancel a confirmed/requested lunch record. Please contact admin."))
            
            if rec.state not in ('draft', 'confirmed', 'requested'):
                raise exceptions.UserError(_("Only draft, requested, or confirmed records can be cancelled."))
        
        self.write({'state': 'cancelled'})
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Cancelled',
                'message': 'Lunch record has been cancelled.',
                'type': 'warning',
                'sticky': False,
                'next': {
                    'type': 'ir.actions.act_window_close',
                }
            }
        }
    
    def action_reset_draft(self):
        if not self.env.user.has_group('base.group_system'):
            raise exceptions.AccessError(_("Only Admin can reset to draft."))
        self.write({'state': 'draft'})
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Reset to Draft',
                'message': 'Record has been reset to draft state.',
                'type': 'info',
                'sticky': False,
                'next': {
                    'type': 'ir.actions.act_window_close',
                }
            }
        }
    
    def action_request_admin_fill(self):
        """Request admin to fill lunch record on behalf of employee - Change state to requested"""
        self.ensure_one()
        
        if self.state != 'draft':
            raise exceptions.UserError(_("Only draft records can be requested."))
        
        # Change state to requested
        self.write({'state': 'requested'})
        
        # Post message in chatter
        message = _(
            '<p><strong>🔔 Admin Fill Request</strong></p>'
            '<p>Employee <strong>%s</strong> has requested admin assistance for:</p>'
            '<ul>'
            '<li>Date: <strong>%s</strong></li>'
            '<li>Day: <strong>%s</strong></li>'
            '<li>Lunch Type: <strong>%s</strong></li>'
            '</ul>'
            '<p>Please confirm this record or use "Admin Fill Record" to create it.</p>'
        ) % (self.employee_id.name, self.date, self.day, self.lunch_type.lunch_type)
        
        self.message_post(
            body=message,
            message_type='notification',
            subtype_xmlid='mail.mt_comment'
        )
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': '✅ Request Sent',
                'message': 'Your request has been submitted. Admin will process it soon.',
                'type': 'success',
                'sticky': False,
                'next': {'type': 'ir.actions.act_window_close'}
            }
        }

    @api.model
    def action_open_lunch_records_all(self):
        """Open All Lunch Records - Admin sees only CONFIRMED records (permanently, not filter)"""
        action = self.env.ref('19_lunch_management.action_lunch_record_all').read()[0]
        
        # Admin sees only confirmed records + today filter
        if self.env.user.has_group('base.group_system'):
            # Get current user's employee record for admin's own drafts
            admin_employee = self.env['hr.employee'].search([
                ('user_id', '=', self.env.uid)
            ], limit=1)
            
            # Domain: Show confirmed records OR admin's own drafts
            if admin_employee:
                domain = [
                    '|',
                    ('state', '=', 'confirmed'),
                    '&',
                    ('employee_id', '=', admin_employee.id),
                    ('state', '=', 'draft')
                ]
            else:
                # If admin has no employee record, only show confirmed
                domain = [('state', '=', 'confirmed')]
            
            action['domain'] = domain
            action['context'] = {'search_default_filter_today': 1}
        
        return action
    
    @api.depends('employee_id', 'date')
    def _compute_name(self):
        for rec in self:
            if rec.employee_id and rec.date:
                rec.name = f"{rec.employee_id.name} - {rec.date.strftime('%Y-%m-%d')}"
            else:
                rec.name = "New"

    def name_get(self):
        result = []
        for rec in self:
            name = f"{rec.employee_id.name} - {rec.date.strftime('%Y-%m-%d')}"
            result.append((rec.id, name))
        return result
    
    @api.onchange('date')
    def _onchange_date_auto_lunch_type(self):
        """Auto-select Veg / Non-Veg based on weekday + block Saturday"""
        if not self.date:
            self.lunch_type = False
            return

        weekday = self.date.weekday()

        # Saturday = Holiday → block + warning (unless admin)
        if weekday == 5 and not self.env.user.has_group('base.group_system'):
            self.lunch_type = False
            return {
                'warning': {
                    'title': "Holiday",
                    'message': "Saturday is a holiday. No lunch record allowed.",
                }
            }

        # Monday & Friday → Non-Veg, rest → Veg
        target_name = "Non-Veg" if weekday in (0, 4) else "Veg"

        lunch_type = self.env['lunch.types'].search([('lunch_type', '=', target_name)], limit=1)
        if lunch_type:
            self.lunch_type = lunch_type.id
        else:
            self.lunch_type = False


class LunchAdminFillWizard(models.TransientModel):
    _name = 'lunch.admin.fill.wizard'
    _description = 'Admin Fill Lunch Record Wizard'

    employee_id = fields.Many2one('hr.employee', string='Employee', required=True)
    date = fields.Date(string='Date', required=True, default=fields.Date.context_today)
    lunch_type = fields.Many2one('lunch.types', string='Lunch Type', required=True)
    note = fields.Text(string='Remarks')

    @api.onchange('date')
    def _onchange_date_lunch_type(self):
        """Auto-select lunch type based on weekday"""
        if self.date:
            weekday = self.date.weekday()
            target_name = "Non-Veg" if weekday in (0, 4) else "Veg"
            lunch_type = self.env['lunch.types'].search([('lunch_type', '=', target_name)], limit=1)
            if lunch_type:
                self.lunch_type = lunch_type.id

    def action_create_record(self):
        """Create lunch record on behalf of employee"""
        self.ensure_one()
        
        # Check if record already exists
        existing = self.env['lunch.record'].search([
            ('employee_id', '=', self.employee_id.id),
            ('date', '=', self.date),
            ('state', '!=', 'cancelled')
        ], limit=1)
        
        if existing:
            raise exceptions.ValidationError(
                _('Lunch record already exists for %s on %s') % (self.employee_id.name, self.date)
            )
        
        # Create record
        record = self.env['lunch.record'].create({
            'employee_id': self.employee_id.id,
            'date': self.date,
            'lunch_type': self.lunch_type.id,
            'note': self.note or 'Created by admin',
            'is_admin_request': True,
            'state': 'confirmed'  # Auto-confirm admin-created records
        })
        
        # Close any pending activities for this request
        activities = self.env['mail.activity'].search([
            ('res_model', '=', 'lunch.record'),
            ('summary', 'ilike', self.employee_id.name)
        ])
        activities.action_done()
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Success',
                'message': f'Lunch record created for {self.employee_id.name} on {self.date}',
                'type': 'success',
                'sticky': False,
                'next': {'type': 'ir.actions.act_window_close'}
            }
        }