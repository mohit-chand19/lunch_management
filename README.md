# Lunch Management System for Odoo 19

A comprehensive employee lunch tracking module for Odoo 19 that helps organizations manage and monitor daily lunch records with cost tracking, time-based confirmations, automated email reminders, bulk import capabilities, late confirmation requests, complete audit trails, and detailed reporting.

## 📋 Features

### Core Functionality
- **Employee Lunch Records**: Track daily lunch consumption by employees
- **Advanced State Management**: Draft → Confirmed → Cancelled → Requested workflow
- **Time-Based Confirmation**: Restrict lunch confirmation to configurable time windows
- **Automatic Employee Detection**: Auto-assigns logged-in employee to lunch records
- **Duplicate Prevention**: One lunch record per employee per day
- **Cost Tracking**: Automatic cost calculation from lunch types
- **Smart Day Detection**: Automatically selects Veg/Non-Veg based on weekdays
- **Holiday Management**: Automatically blocks Saturday entries
- **Dual Date System**: Separate lunch date and confirmation timestamp

### 🆕 Chatter & Activity Tracking
- **Complete Audit Trail**: Full conversation history on every lunch record
- **Automatic Message Posting**: System posts messages for all actions:
  - Record creation, confirmation, cancellation
  - State changes by admin or employee
  - Lunch type modifications
  - Late confirmation requests
  - Request approvals/rejections
- **User Attribution**: All messages include user name, role (Admin/Employee/Lunch Manager), date, and time
- **Activity Notifications**: Admins receive activity alerts for late confirmation requests
- **Follower System**: Users can follow records to get updates
- **File Attachments**: Attach documents or images to records

### 🆕 Late Confirmation Request System
- **Request Workflow**: Employees can request admin approval after deadline
- **"Requested" State**: New state for pending late confirmation requests
- **Reason Field**: Employees must provide reason for late request
- **Admin Approval Panel**: Dedicated "Pending Requests" menu for admins
- **Two-Action System**:
  - **Fill for Employee**: Admin approves and confirms lunch
  - **Reject Request**: Admin denies and cancels record
- **Activity Management**: Auto-creates activities for all admins on new requests
- **Complete Audit**: All actions logged in chatter with timestamps

### 🆕 Lunch Manager Role
- **Delegated Authority**: Admin can assign Lunch Manager role to any user
- **Full Permissions**: Lunch Managers have admin-level access for lunch module
- **Flexible Assignment**: Multiple users can be Lunch Managers
- **Capabilities**:
  - View all lunch records
  - Approve/reject late confirmation requests
  - Fill lunch records for employees
  - Cancel any record (draft/confirmed/requested)
  - Reset records to draft
  - Configure lunch types and timing
  - Access email scheduler and import tools

### 🆕 Email Reminder System
- **Automated Daily Reminders**: Send lunch reminder emails to all employees at configured time
- **Beautiful HTML Templates**: Professional, responsive email design with call-to-action buttons
- **Timezone Support**: Nepal Time (Asia/Kathmandu) with configurable send times
- **Test Email Function**: Send test emails before enabling for all employees
- **Manual Trigger**: Admins can manually send emails anytime
- **Scheduled Jobs**: Automatic cron job runs hourly to check and send emails
- **Direct Links**: Emails include direct links to lunch form for easy access

### 🆕 Excel Import Feature
- **Bulk Historical Import**: Import past lunch records from Excel files
- **Template Download**: Pre-formatted Excel template with sample data
- **Smart Validation**: 
  - Validates employee names against HR records
  - Checks date formats and lunch types
  - Auto-skips Saturday records (holidays)
  - Updates existing records if duplicates found
- **Detailed Reports**: Shows success count, errors, and skipped records
- **Error Handling**: Clear error messages with row numbers for easy correction
- **State Management**: Import records in draft, confirmed, or cancelled states

### 🆕 Enhanced Date Management
- **Tomorrow by Default**: New records default to next day for better planning
- **No Backward Selection**: Employees cannot select past dates
- **Dual Date System**:
  - **Lunch Date**: The actual day for lunch service
  - **Confirmed Date & Time**: Exact timestamp when lunch was confirmed
- **Admin Override**: Admins can create past records for corrections
- **Auto-Save Timestamp**: Confirmation time automatically recorded

### User Roles & Permissions
- **Employees**: Create and confirm their own lunch records
- **Lunch Managers** : 
  - Designated users with admin-level lunch permissions
  - Approve late confirmation requests
  - Fill records for employees
  - Full access to configurations
- **Administrators**: 
  - Full access to all records, configurations, and reports
  - Assign Lunch Manager role to users
  - Email scheduler configuration
  - Excel import capabilities
  - Advanced reporting features

### Multiple View Types
- **List View**: Traditional table with sortable columns and sum totals
- **Kanban View**: Card-based layout grouped by state, mobile-friendly
- **Calendar View**: Monthly/weekly calendar with color-coded states
- **Graph View**: Bar/line/pie charts for cost visualization
- **Pivot View**: Cross-tabulation analysis with drag-and-drop

### Reporting
- **Interactive Reports**: Filtered list view with grouping options
- **PDF Reports**: Professional formatted reports with:
  - Single employee or all employees view
  - Date range filtering
  - Cost summaries and grand totals
  - Automatic currency formatting
  - Company branding
  - Confirmed vs draft distinction

### Configuration
- **Lunch Types**: Define multiple lunch categories with costs (Veg/Non-Veg)
- **Timing Settings**: Configure allowed confirmation hours (Nepal timezone)
- **Email Scheduler**: Configure automated email reminder timing and templates
- **Access Control**: Role-based permissions with Lunch Manager delegation
- **Activity Management**: Automated notifications and follow-ups

## 🚀 Installation

### Prerequisites
```bash
# Install required Python packages
pip install pandas openpyxl pytz
```

### Installation Steps

1. Download or clone this repository to your Odoo addons directory:
   ```bash
   cd /path/to/odoo/addons
   git clone https://github.com/mohit-chand19/lunch_management.git
   ```

2. Restart Odoo server:
   ```bash
   sudo systemctl restart odoo
   # OR
   ./odoo-bin
   ```

3. Update the addons list in Odoo:
   - Go to Apps menu
   - Click "Update Apps List"
   - Search for "Lunch Management"
   - Click Install

4. Configure email server (required for email reminders):
   - Go to **Settings → Technical → Outgoing Mail Servers**
   - Configure your SMTP settings:
     - **Gmail**: smtp.gmail.com, Port 587, TLS
     - **Outlook**: smtp.office365.com, Port 587, TLS
     - Use app-specific passwords for Gmail

5. Configure the module:
   - Navigate to **Lunch Management → Configuration → Lunch Types**
     - Add "Veg" with cost (e.g., Rs. 100)
     - Add "Non-Veg" with cost (e.g., Rs. 150)
   - Navigate to **Lunch Management → Configuration → Lunch Timing Setting**
     - Set start time: 9:00 AM
     - Set end time: 11:00 AM
   - Navigate to **Lunch Management → Configuration → Email Scheduler**
     - Configure email send time
     - Test email functionality

6. Assign Lunch Manager role (optional):
   - Go to **Settings → Users & Companies → Users**
   - Open user profile
   - Under **"Human Resources"** tab, check **"Lunch Manager"**
   - Save

## 📦 Module Structure

```
19_lunch_management/
├── __init__.py
├── __manifest__.py
├── models/
│   ├── __init__.py
│   ├── lunch_record.py           # Main model with chatter 
│   ├── lunch_types.py            # Lunch types configuration
│   ├── lunch_timing.py           # Time window configuration
│   ├── lunch_report_wizard.py   # Report generation wizard
│   ├── lunch_email_scheduler.py # Email reminder system
│   └── lunch_excel_import.py    # Excel import wizard
├── views/
│   ├── lunch_record_views.xml   # All views + chatter 
│   ├── lunch_report_views.xml   # Report wizard views
│   └── lunch_email_views.xml    # Email & import views
├── data/
│   └── lunch_email_data.xml     # Email templates & config
├── reports/
│   └── lunch_report.xml         # PDF report template
├── security/
│   ├── lunch_security.xml       # Security rules + Lunch Manager 
│   └── ir.model.access.csv      # Access rights 
└── static/
    └── description/
        └── icon.png              # Module icon
```

## 🎯 Usage

### For Employees

#### 1. **Create Lunch Record**:
   - Go to **Lunch Management → Lunch Records → My Lunch Records**
   - Click Create
   - Date defaults to **tomorrow** (auto-selected)
   - Lunch type auto-selected based on day (Veg/Non-Veg)
   - Add optional remarks
   - Save (record created in Draft state)

#### 2. **Confirm Lunch (Within Time Window)**:
   - Open your draft lunch record
   - Click "Confirm" button (during configured hours: 9-11 AM)
   - Confirmation timestamp automatically saved
   - Record moves to Confirmed state
   - Message posted to chatter: "Lunch confirmed by Employee (Your Name) on [timestamp]"
   - Record becomes non-editable

#### 3. **Request Late Confirmation** :
   - If you miss the confirmation deadline
   - Open your draft lunch record
   - Enter reason in **"Request Reason"** field
   - Click **"Request Late Confirmation"** button
   - Record moves to "Requested" state (orange badge)
   - Admin receives activity notification
   - Message posted to chatter with your reason
   - Wait for admin approval
   - Check chatter for admin's response

#### 4. **View Message History**:
   - Open any lunch record
   - Scroll to bottom to see **Chatter**
   - View all actions, changes, and communications
   - See who did what and when

#### 5. **Receive Email Reminders**:
   - Receive daily reminder emails at 2:00 PM (configurable)
   - Click "Fill Lunch Form" button in email
   - Redirected to your lunch records page

### For Lunch Managers 

Lunch Managers are designated employees with admin-level permissions for lunch management:

#### 1. **View All Records**:
   - Access **Lunch Management → Lunch Records → All Lunch Records**
   - See confirmed and requested records from all employees
   - Use filters: Today, Tomorrow, This Week, This Month
   - Group by Employee, Date, or Status

#### 2. **Handle Pending Requests**:
   - Go to **Lunch Management → Lunch Records → Pending Requests**
   - See all late confirmation requests
   - Open record to view:
     - Employee name
     - Lunch date
     - Request reason in chatter
   - Choose action:
     - **"Fill for Employee"** - Approve and confirm
     - **"Reject Request"** - Deny and cancel
   - Action logged in chatter with your name and timestamp

#### 3. **Fill Lunch for Employees**:
   - Open requested record
   - Review reason in chatter
   - Click **"Fill for Employee"** button
   - Lunch confirmed with current timestamp
   - Message posted: "Lunch filled by Lunch Manager (Your Name)"
   - Activity marked as complete

#### 4. **Manage Configurations**:
   - Access all configuration menus
   - Modify lunch types and costs
   - Adjust timing settings
   - Configure email scheduler
   - Import historical data from Excel

### For Administrators

#### 1. **View All Records**:
   - Go to **Lunch Management → Lunch Records → All Lunch Records**
   - Automatically filtered to show:
     - Today's date
     - Confirmed and Requested records only
     - Admin's own draft records (if any)
   - Can remove filters to see draft/cancelled if needed
   - Switch between List, Kanban, Calendar, Graph, Pivot views

#### 2. **Generate Reports**:
   - Go to **Lunch Management → Reporting → Lunch Report**
   - Select date range
   - Choose "All Employees" or "Specific Employee"
   - Click "View Report" for interactive view
   - Click "Print PDF" for download
   - Reports show confirmed records with costs

#### 3. **Manage Pending Requests** :
   - Go to **Lunch Management → Lunch Records → Pending Requests**
   - See all late confirmation requests
   - Badge count shows pending items
   - Open record to review:
     - Request reason (in chatter)
     - Employee details
     - Request date/time
   - Take action:
     - **"Fill for Employee"** - Approve
     - **"Reject Request"** - Deny
   - All actions logged in chatter

#### 4. **Assign Lunch Manager Role** :
   - Go to **Settings → Users & Companies → Users**
   - Select employee user
   - Under **"Human Resources"** tab
   - Check **"Lunch Manager"** checkbox
   - Save
   - User now has admin-level lunch permissions
   - Can manage multiple Lunch Managers

#### 5. **Configure Email Reminders**:
   - Go to **Lunch Management → Configuration → Email Scheduler**
   - Set email send time (e.g., 14.0 = 2:00 PM)
   - Click "Send Test Email" to test configuration
   - Click "Send Now to All" to manually trigger emails
   - Monitor "Last Sent Date" to verify automatic sending

#### 6. **Import Historical Data**:
   - Go to **Lunch Management → Configuration → Import from Excel**
   - Click "Download Template" to get Excel format
   - Fill Excel file with columns:
     - Employee Name (must match HR records)
     - Date (YYYY-MM-DD format)
     - Lunch Type (Veg/Non-Veg)
     - State (draft/confirmed/cancelled)
     - Remarks (optional)
   - Upload completed Excel file
   - Click "Import" and review results
   - Check for errors and fix if needed

#### 7. **Monitor Activities**:
   - Check activity notifications
   - See pending late confirmation requests
   - Mark activities as done after handling
   - Track resolution time

#### 8. **Audit Trail Review**:
   - Open any lunch record
   - View chatter for complete history
   - See all changes with user names and timestamps
   - Export reports with confirmed dates
   - Analyze patterns and compliance

## 🔒 Security & Permissions

### Access Rights
| Model | Employee | Lunch Manager | Administrator |
|-------|----------|-------------------|---------------|
| Lunch Records | Read/Write (own only) | Full Access (all) | Full Access (all) |
| Lunch Types | Read Only | Full Access | Full Access |
| Lunch Timing | Read Only | Full Access | Full Access |
| Email Scheduler | No Access | Full Access | Full Access |
| Excel Import | No Access | Full Access | Full Access |
| Reports | Own Records | All Records | All Records |
| Pending Requests | No Access | Full Access | Full Access |
| Assign Lunch Manager | No Access | No Access | Full Access |

### User Capabilities by Role

#### Regular Employee:
```
✅ Create lunch records (for tomorrow by default)
✅ Confirm own lunch (within time window)
✅ Request late confirmation (with reason)
✅ Cancel own draft records
✅ View own record history in chatter
✅ Receive email reminders
✅ View own reports
❌ View other employees' draft records
❌ Approve late requests
❌ Cancel confirmed records
❌ Reset records to draft
❌ Delete any records
```

#### Lunch Manager ⭐NEW:
```
✅ All employee capabilities
✅ View all confirmed/requested records
✅ View pending late confirmation requests
✅ Approve late confirmation requests
✅ Fill lunch records for employees
✅ Reject late confirmation requests
✅ Cancel any record (draft/confirmed/requested)
✅ Reset records to draft
✅ Configure lunch types and costs
✅ Adjust timing settings
✅ Configure email scheduler
✅ Import from Excel
✅ Generate reports for all employees
✅ Delete any records
❌ Assign Lunch Manager role to others
```

#### Administrator:
```
✅ All Lunch Manager capabilities
✅ Assign Lunch Manager role to any user
✅ Create records for past dates
✅ Full system configuration access
✅ Manage all security settings
```

### Business Rules
- Employees cannot edit confirmed lunch records
- Employees cannot delete any lunch records
- Employees cannot select past dates
- Only Lunch Managers/Admins can delete records
- Only Lunch Managers/Admins can reset records to draft
- Only Lunch Managers/Admins can approve late requests
- Confirmation only allowed within configured time window
- One lunch record per employee per day (excluding cancelled)
- Saturday entries are blocked (holiday)
- Emails sent once per day at configured time
- All changes tracked in chatter with user attribution

## ⚙️ Technical Details

### Dependencies
- `base` - Odoo base module
- `hr` - Human Resources module
- `mail` - Email and chatter functionality
- **Python packages**: `pandas`, `openpyxl`, `pytz`

### Database Models
- `lunch.record` - Main lunch tracking model (with mail.thread, mail.activity.mixin)
- `lunch.types` - Lunch type master data
- `lunch.timing` - Configuration for time windows
- `lunch.report.wizard` - Transient model for report generation
- `lunch.email.scheduler` - Email reminder configuration
- `lunch.excel.import` - Excel import wizard

### Key Fields

**Lunch Record**:
- `state`: Selection (draft/confirmed/cancelled/requested) 
- `employee_id`: Many2one (hr.employee) - tracked
- `date`: Date field - Lunch date (default: tomorrow)
- `confirmed_date`: Datetime field - Confirmation timestamp 
- `lunch_type`: Many2one (lunch.types) - Auto-selected by weekday, tracked
- `cost`: Related field from lunch type
- `day`: Computed day name
- `note`: Text field - tracked
- `request_reason`: Text field - Reason for late request 
- `requested_by`: Many2one (res.users) - Who requested 
- `approved_by`: Many2one (res.users) - Who approved 

**Email Scheduler**:
- `email_time`: Float (24-hour format, e.g., 14.0 = 2:00 PM)
- `email_template_id`: Many2one (mail.template)
- `is_active`: Boolean
- `last_sent_date`: Date (tracks last successful send)

**Excel Import**:
- `excel_file`: Binary field for file upload
- `import_results`: Text field showing import summary
- `state`: Selection (draft/done)

### Chatter Integration ⭐NEW
**Inheritance**:
```python
_inherit = ['mail.thread', 'mail.activity.mixin']
```

**Tracking**:
- All important field changes tracked
- Automatic message posting on actions
- User and timestamp attribution
- Activity creation for admin notifications

**Messages Posted**:
1. Record creation
2. Record confirmation (with user and timestamp)
3. State changes
4. Field modifications
5. Late confirmation requests
6. Request approvals/rejections
7. Admin fills for employee
8. Cancellations and resets

### Automation
**Cron Job**: "Send Lunch Reminder Emails"
- Runs every 1 hour
- Checks if current time matches configured send time
- Sends emails to all active employees with work email
- Updates last sent date to prevent duplicate sends
- Logs all activities for troubleshooting

### Timezone
The module uses **Asia/Kathmandu** timezone for:
- Time-based confirmations
- Email scheduling
- Report timestamps
- Confirmed date/time recording

Modify in code if needed:
```python
nepal_tz = pytz.timezone('Asia/Kathmandu')
```

### Email Configuration Examples

**Gmail**:
```
SMTP Server: smtp.gmail.com
Port: 587
Security: TLS (STARTTLS)
Username: your-email@gmail.com
Password: [App Password - Generate at https://myaccount.google.com/apppasswords]
```

**Outlook/Office 365**:
```
SMTP Server: smtp.office365.com
Port: 587
Security: TLS (STARTTLS)
Username: your-email@company.com
Password: [Your password]
```

## 🔄 Workflows

### Standard Confirmation Workflow
```
1. Employee creates lunch record
   ↓
2. Date defaults to tomorrow
   ↓
3. Lunch type auto-selected (Veg/Non-Veg)
   ↓
4. Employee adds optional remarks
   ↓
5. Chatter posts: "Record created"
   ↓
6. Employee clicks "Confirm" (9-11 AM window)
   ↓
7. System saves confirmation timestamp
   ↓
8. State → Confirmed
   ↓
9. Chatter posts: "Lunch confirmed by Employee (Name) on [timestamp]"
   ↓
10. Record locked (non-editable)
```

### Late Confirmation Request Workflow ⭐NEW
```
1. Employee misses confirmation deadline (after 11 AM)
   ↓
2. Opens draft lunch record
   ↓
3. Clicks "Request Late Confirmation" button
   ↓
4. Enters reason: "Was in meeting, forgot to confirm"
   ↓
5. Submits request
   ↓
6. State → Requested (orange badge)
   ↓
7. Chatter posts: "Late confirmation requested by [Name]"
   ↓
8. Activity created for all Admins/Lunch Managers
   ↓
9. Admin/Manager receives notification
   ↓
10. Reviews request in "Pending Requests" menu
   ↓
11. Reads reason in chatter
   ↓
12. Admin chooses:
    Option A: Click "Fill for Employee"
      → State → Confirmed
      → Confirmation timestamp saved
      → Chatter posts: "Lunch filled by Admin (Name)"
      → Activity marked complete
    Option B: Click "Reject Request"
      → State → Cancelled
      → Chatter posts: "Request rejected by Admin (Name)"
      → Activity marked complete
   ↓
13. Employee sees result in chatter
```

### Email Reminder Workflow
```
Daily at 2:00 PM (configurable):
1. Cron job runs
   ↓
2. Checks if emails already sent today (skips if yes)
   ↓
3. Loops through all active employees
   ↓
4. Gets employees with work_email
   ↓
5. Sends personalized HTML email to each
   ↓
6. Email includes:
   - Employee name
   - Tomorrow's date
   - Direct link to lunch form
   ↓
7. Updates "Last Sent Date"
   ↓
8. Logs: "Email sent to [Name] ([email])"
   ↓
9. Employee receives email
   ↓
10. Clicks "Fill Lunch Form" button
   ↓
11. Redirected to "My Lunch Records"
```

## 📊 Excel Import Format

### Required Columns
| Column Name | Format | Example | Required |
|------------|--------|---------|----------|
| Employee Name | Text | John Doe | Yes |
| Date | YYYY-MM-DD | 2024-12-09 | Yes |
| Lunch Type | Text | Veg or Non-Veg | Yes |
| State | Text | confirmed | Yes |
| Remarks | Text | Extra spicy | No |

### Sample Data
```
Employee Name | Date       | Lunch Type | State     | Remarks
John Doe      | 2024-12-09 | Non-Veg    | confirmed | 
Jane Smith    | 2024-12-09 | Veg        | confirmed | Extra spicy
John Doe      | 2024-12-10 | Veg        | confirmed |
```

### Import Rules
- Employee names must match exactly with HR records
- Dates must be in YYYY-MM-DD format
- Saturday records are automatically skipped
- Duplicate records (same employee + date) will be updated
- Invalid employee names or dates will be logged as errors
- Confirmation timestamp not set for imported records (historical data)

## 📧 Email Template Customization

The default email template includes:
- Personalized greeting with employee name
- Tomorrow's date
- Call-to-action button linking to lunch form
- Professional responsive design
- Company branding

To customize:
1. Go to **Settings → Technical → Email Templates**
2. Search for "Lunch Reminder Email"
3. Edit HTML content as needed
4. Available variables:
   - `${object.name}` - Employee name
   - `${object.work_email}` - Employee email
   - `${object.company_id.name}` - Company name
   - `${ctx.get('lunch_url')}` - Link to lunch form

## 🧪 Testing

### Test Chatter Functionality ⭐NEW
1. Create a lunch record
2. Check chatter shows creation message
3. Confirm record
4. Verify confirmation message with timestamp
5. Admin resets to draft
6. Check reset message appears
7. Verify user names and roles shown

### Test Late Confirmation Request ⭐NEW
1. Create lunch record at 2 PM (after deadline)
2. Enter reason in "Request Reason" field
3. Click "Request Late Confirmation"
4. Verify state changes to "Requested" (orange)
5. Check chatter shows request with reason
6. Login as Admin
7. Go to "Pending Requests" menu
8. See request in list
9. Open record
10. Click "Fill for Employee"
11. Verify confirmation with timestamp
12. Check chatter shows admin action

### Test Lunch Manager Role ⭐NEW
1. Login as Admin
2. Go to Settings → Users
3. Assign "Lunch Manager" to a user
4. Login as that user
5. Verify access to:
   - All Lunch Records
   - Pending Requests
   - Configuration menus
6. Test approval workflow
7. Verify cannot assign Lunch Manager role

### Test Date Features ⭐NEW
1. Create new lunch record
2. Verify date defaults to tomorrow
3. Try to select yesterday (should fail)
4. Confirm record within time window
5. Check "Confirmed Date & Time" field populated
6. Verify timestamp accurate

### Test Email Functionality
1. Ensure you have an employee record with work email
2. Configure SMTP server
3. Open Email Scheduler configuration
4. Click "Send Test Email"
5. Check your inbox

### Test Excel Import
1. Download template from Import wizard
2. Add 5-10 sample records
3. Upload and import
4. Verify records created correctly
5. Try importing same file again (should update existing)

### Test Automation
1. Set email time to 5 minutes from now
2. Wait for cron job to run
3. Check if emails are sent
4. Verify "Last Sent Date" is updated

### Test Multiple Views
1. Open "All Lunch Records"
2. Switch to Kanban view
3. Switch to Calendar view
4. Switch to Graph view
5. Switch to Pivot view
6. Verify data displays correctly in all views

## 🐛 Known Issues & Limitations

### Notes:
1. **Timezone**: All times use Nepal timezone (Asia/Kathmandu)
2. **Activities**: Require mail module to be installed
3. **Chatter**: Automatic with mail.thread inheritance
4. **Past dates**: Admin can still create for corrections
5. **Lunch Manager**: Equal to Admin for lunch module only
6. **Confirmed date**: Cannot be manually changed (system-set only)
7. **One request per record**: Cannot re-request after rejection

### Limitations:
- Timing configuration is global (not per employee or department)
- Single lunch per employee per day (no multiple meals)
- Time validation uses Nepal timezone (hardcoded)
- Email sending limited by SMTP server rate limits
- Excel import requires exact employee name match
- Saturday is hardcoded as holiday
- Cannot edit confirmed lunch (by design)
- Activities sent to all admins/managers (not individually assignable)

## 🔄 Future Enhancements

- [ ] Multi-timezone support for different office locations
- [ ] Mobile app integration
- [ ] SMS notifications alongside emails
- [ ] Monthly summary dashboard with charts
- [ ] Department-wise lunch limits and budgets
- [ ] Integration with payroll for automatic deductions
- [ ] Multiple meal times (breakfast, lunch, dinner)
- [ ] Configurable holidays calendar
- [ ] Employee dietary preferences tracking
- [ ] Lunch menu planning and voting system
- [ ] Advanced analytics and reporting
- [ ] Multi-company support
- [ ] Custom email templates per department
- [ ] Approval hierarchy (multi-level approvals)
- [ ] Budget allocation and tracking

## 📄 License

This module is licensed under LGPL-3. See [LICENSE](LICENSE) file for details.

## 👨‍💻 Author

**Innovax Solutions Pvt Ltd**

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📞 Support

For issues, questions, or suggestions:
- Open an issue on GitHub
- Contact: Innovax Solutions Pvt Ltd
- Check logs: `/var/log/odoo/odoo.log` for troubleshooting
- Enable debug mode: Add `?debug=1` to URL for detailed errors

## 🙏 Acknowledgments

- Built for Odoo 19 Community/Enterprise Edition
- Uses Odoo's QWeb reporting engine
- Email templates based on responsive HTML design
- Excel import powered by pandas library
- Chatter functionality via mail.thread
- Activity management via mail.activity.mixin
- Inspired by organizational lunch management needs

## 🔧 Troubleshooting

### Chatter Not Showing
- Verify mail module is installed
- Check model inherits mail.thread
- Clear browser cache
- Restart Odoo server

### Late Confirmation Requests Not Working
- Verify "Requested" state in state selection
- Check user has employee record
- Verify admin receives activities
- Check "Pending Requests" menu appears

### Lunch Manager Role Not Working
- Verify security groups installed
- Check user assigned "Lunch Manager" role
- Clear browser cache
- Re-login user

### Date Defaulting to Today Instead of Tomorrow
- Check date field default value
- Verify timedelta import
- Clear form cache

### Confirmed Date Not Saving
- Verify field is Datetime type
- Check write() method includes confirmed_date
- Verify timezone configuration

### Activities Not Created
- Check mail.activity.mixin inheritance
- Verify activity_schedule() call
- Check admin users exist
- Verify mail module installed

### Emails Not Sending
- Verify SMTP configuration in Settings
- Check "Send Test Email" works
- Ensure cron job is active
- Check Odoo logs for errors
- Verify employees have work email addresses

### Excel Import Errors
- Install pandas: `pip install pandas openpyxl`
- Restart Odoo after installing packages
- Ensure employee names match exactly
- Use YYYY-MM-DD date format
- Check for Excel file corruption

### Module Won't Upgrade
- Clear browser cache
- Restart Odoo server
- Check file permissions
- Review Odoo logs for specific errors
- Verify all dependencies installed
