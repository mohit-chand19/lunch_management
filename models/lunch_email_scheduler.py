from odoo import models, fields, api
from datetime import datetime, timedelta
import pytz
import logging

_logger = logging.getLogger(__name__)


class LunchEmailScheduler(models.Model):
    _name = 'lunch.email.scheduler'
    _description = 'Lunch Email Scheduler Configuration'

    name = fields.Char(string='Name', default='Lunch Reminder Configuration', readonly=True)
    email_time = fields.Float(string='Email Time (Hours)', default=14.0, required=True,
                               help='Time in 24-hour format (e.g., 14.0 = 2:00 PM)')
    email_template_id = fields.Many2one('mail.template', string='Email Template',
                                        domain=[('model', '=', 'hr.employee')])
    is_active = fields.Boolean(string='Active', default=True)
    last_sent_date = fields.Date(string='Last Sent Date', readonly=True)
    
    _sql_constraints = [
        ('unique_scheduler', 'unique(name)', 'Only one scheduler configuration allowed!')
    ]

    def _send_lunch_reminder_emails(self):
        """Scheduled action to send lunch reminder emails to all employees"""
        _logger.info("Starting lunch reminder email process...")
        
        # Get active scheduler config
        scheduler = self.search([('is_active', '=', True)], limit=1)
        if not scheduler:
            _logger.warning("No active lunch email scheduler found!")
            return
        
        # Check if already sent today
        today = fields.Date.today()
        if scheduler.last_sent_date == today:
            _logger.info("Emails already sent today. Skipping...")
            return
        
        # Get Nepal timezone and check current time
        nepal_tz = pytz.timezone('Asia/Kathmandu')
        now = datetime.now(nepal_tz)
        current_hour = now.hour + (now.minute / 60.0)
        
        # Check if it's time to send (within 1 hour window)
        if not (scheduler.email_time <= current_hour <= scheduler.email_time + 1):
            _logger.info(f"Not time to send yet. Current: {current_hour}, Target: {scheduler.email_time}")
            return
        
        # Get all active employees with email
        employees = self.env['hr.employee'].search([
            ('active', '=', True),
            ('work_email', '!=', False)
        ])
        
        if not employees:
            _logger.warning("No employees with email found!")
            return
        
        # Get email template
        template = scheduler.email_template_id
        if not template:
            # Create default template if not exists
            template = self._create_default_email_template()
            scheduler.email_template_id = template.id
        
        # Get base URL
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        
        sent_count = 0
        failed_count = 0
        
        for employee in employees:
            try:
                # Prepare context with employee-specific data
                ctx = {
                    'employee_name': employee.name,
                    'tomorrow_date': (datetime.now() + timedelta(days=1)).strftime('%B %d, %Y'),
                    'lunch_url': f"{base_url}/web#action=19_lunch_management.action_lunch_record_my",
                }
                
                # Send email
                template.with_context(ctx).send_mail(
                    employee.id,
                    force_send=True,
                    email_values={'email_to': employee.work_email}
                )
                sent_count += 1
                _logger.info(f"Email sent to {employee.name} ({employee.work_email})")
                
            except Exception as e:
                failed_count += 1
                _logger.error(f"Failed to send email to {employee.name}: {str(e)}")
        
        # Update last sent date
        scheduler.last_sent_date = today
        
        _logger.info(f"Lunch reminder email process completed. Sent: {sent_count}, Failed: {failed_count}")

    def _create_default_email_template(self):
        """Create default email template for lunch reminders"""
        template = self.env['mail.template'].create({
            'name': 'Lunch Reminder Email',
            'model_id': self.env['ir.model'].search([('model', '=', 'hr.employee')], limit=1).id,
            'subject': 'Lunch Reminder - Fill Tomorrow\'s Form',
            'body_html': '''
                <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; background-color: #f5f5f5;">
                    <div style="background-color: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                        <h2 style="color: #2c3e50; margin-bottom: 20px;">🍽️ Lunch Reminder</h2>
                        
                        <p style="color: #34495e; font-size: 16px; line-height: 1.6;">
                            Hello <strong>${ctx.get('employee_name', 'Employee')}</strong>,
                        </p>
                        
                        <p style="color: #34495e; font-size: 16px; line-height: 1.6;">
                            This is a friendly reminder to fill in your lunch form for <strong>${ctx.get('tomorrow_date', 'tomorrow')}</strong>.
                        </p>
                        
                        <div style="text-align: center; margin: 30px 0;">
                            <a href="${ctx.get('lunch_url', '#')}" 
                               style="display: inline-block; padding: 15px 40px; background-color: #3498db; color: white; 
                                      text-decoration: none; border-radius: 5px; font-size: 16px; font-weight: bold;">
                                Fill Lunch Form
                            </a>
                        </div>
                        
                        <p style="color: #7f8c8d; font-size: 14px; line-height: 1.6;">
                            Please make sure to confirm your lunch before the deadline to ensure your meal is prepared.
                        </p>
                        
                        <hr style="border: none; border-top: 1px solid #ecf0f1; margin: 20px 0;" />
                        
                        <p style="color: #95a5a6; font-size: 12px;">
                            This is an automated message. Please do not reply to this email.
                        </p>
                    </div>
                </div>
            ''',
            'auto_delete': False,
        })
        return template

    def action_send_test_email(self):
        """Send test email to current user"""
        self.ensure_one()
        
        employee = self.env['hr.employee'].search([
            ('user_id', '=', self.env.uid)
        ], limit=1)
        
        if not employee or not employee.work_email:
            raise models.ValidationError("Current user has no employee record or email!")
        
        template = self.email_template_id
        if not template:
            template = self._create_default_email_template()
            self.email_template_id = template.id
        
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        
        ctx = {
            'employee_name': employee.name,
            'tomorrow_date': (datetime.now() + timedelta(days=1)).strftime('%B %d, %Y'),
            'lunch_url': f"{base_url}/web#action=19_lunch_management.action_lunch_record_my",
        }
        
        template.with_context(ctx).send_mail(
            employee.id,
            force_send=True,
            email_values={'email_to': employee.work_email}
        )
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Test Email Sent',
                'message': f'Test email sent to {employee.work_email}',
                'type': 'success',
                'sticky': False,
            }
        }

    def action_send_now(self):
        """Manually trigger email sending"""
        self.ensure_one()
        self.last_sent_date = False  # Reset to allow sending
        self._send_lunch_reminder_emails()
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Emails Sent',
                'message': 'Lunch reminder emails have been sent to all employees.',
                'type': 'success',
                'sticky': False,
            }
        }