from odoo import models, fields, api, exceptions, _
from datetime import datetime
import base64
import io
import logging

_logger = logging.getLogger(__name__)

try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False
    _logger.warning("pandas not installed. Excel import will not work.")


class LunchExcelImport(models.TransientModel):
    _name = 'lunch.excel.import'
    _description = 'Import Lunch Records from Excel'

    excel_file = fields.Binary(string='Excel File', required=True,
                                help='Upload Excel file with lunch records')
    filename = fields.Char(string='Filename')
    
    import_results = fields.Text(string='Import Results', readonly=True)
    state = fields.Selection([
        ('draft', 'Upload File'),
        ('done', 'Import Complete')
    ], default='draft')

    def action_import_excel(self):
        """Import lunch records from Excel file"""
        self.ensure_one()
        
        if not PANDAS_AVAILABLE:
            raise exceptions.UserError(
                _("pandas library is not installed. Please install it using: pip install pandas openpyxl")
            )
        
        if not self.excel_file:
            raise exceptions.UserError(_("Please upload an Excel file first!"))
        
        try:
            # Decode the file
            file_data = base64.b64decode(self.excel_file)
            
            # Read Excel file
            df = pd.read_excel(io.BytesIO(file_data))
            
            # Validate columns
            required_columns = ['Employee Name', 'Date', 'Lunch Type', 'State']
            missing_columns = [col for col in required_columns if col not in df.columns]
            
            if missing_columns:
                raise exceptions.UserError(
                    _("Missing required columns: %s\n\nRequired columns are: %s") % 
                    (', '.join(missing_columns), ', '.join(required_columns))
                )
            
            # Process records
            success_count = 0
            error_count = 0
            error_messages = []
            skipped_count = 0
            
            for index, row in df.iterrows():
                try:
                    # Get employee
                    employee_name = str(row['Employee Name']).strip()
                    employee = self.env['hr.employee'].search([
                        ('name', '=ilike', employee_name)
                    ], limit=1)
                    
                    if not employee:
                        error_messages.append(f"Row {index + 2}: Employee '{employee_name}' not found")
                        error_count += 1
                        continue
                    
                    # Parse date
                    try:
                        if isinstance(row['Date'], str):
                            date_obj = datetime.strptime(row['Date'], '%Y-%m-%d').date()
                        else:
                            date_obj = pd.to_datetime(row['Date']).date()
                    except Exception as e:
                        error_messages.append(f"Row {index + 2}: Invalid date format - {row['Date']}")
                        error_count += 1
                        continue
                    
                    # Check if Saturday (holiday)
                    if date_obj.weekday() == 5:
                        skipped_count += 1
                        continue
                    
                    # Get lunch type
                    lunch_type_name = str(row['Lunch Type']).strip()
                    lunch_type = self.env['lunch.types'].search([
                        ('lunch_type', '=ilike', lunch_type_name)
                    ], limit=1)
                    
                    if not lunch_type:
                        error_messages.append(f"Row {index + 2}: Lunch type '{lunch_type_name}' not found")
                        error_count += 1
                        continue
                    
                    # Get state
                    state = str(row['State']).strip().lower()
                    if state not in ['draft', 'confirmed', 'cancelled']:
                        state = 'confirmed'  # Default to confirmed for past records
                    
                    # Check if record already exists
                    existing = self.env['lunch.record'].search([
                        ('employee_id', '=', employee.id),
                        ('date', '=', date_obj),
                        ('state', '!=', 'cancelled')
                    ], limit=1)
                    
                    if existing:
                        # Update existing record
                        existing.sudo().write({
                            'lunch_type': lunch_type.id,
                            'state': state,
                            'note': row.get('Remarks', '') or ''
                        })
                        success_count += 1
                    else:
                        # Create new record
                        self.env['lunch.record'].sudo().create({
                            'employee_id': employee.id,
                            'date': date_obj,
                            'lunch_type': lunch_type.id,
                            'state': state,
                            'note': row.get('Remarks', '') or ''
                        })
                        success_count += 1
                    
                except Exception as e:
                    error_messages.append(f"Row {index + 2}: {str(e)}")
                    error_count += 1
            
            # Prepare results message
            results = f"""
Import completed successfully!

✅ Successfully imported/updated: {success_count} records
❌ Errors: {error_count}
⏭️ Skipped (Saturdays): {skipped_count}

"""
            
            if error_messages:
                results += "\nError Details:\n" + "\n".join(error_messages[:20])
                if len(error_messages) > 20:
                    results += f"\n... and {len(error_messages) - 20} more errors"
            
            self.write({
                'import_results': results,
                'state': 'done'
            })
            
            return {
                'type': 'ir.actions.act_window',
                'res_model': 'lunch.excel.import',
                'res_id': self.id,
                'view_mode': 'form',
                'target': 'new',
            }
            
        except Exception as e:
            raise exceptions.UserError(_("Error reading Excel file: %s") % str(e))

    def action_download_template(self):
        """Download Excel template for lunch records"""
        
        if not PANDAS_AVAILABLE:
            raise exceptions.UserError(
                _("pandas library is not installed. Please install it using: pip install pandas openpyxl")
            )
        
        # Create sample data
        sample_data = {
            'Employee Name': ['John Doe', 'Jane Smith', 'John Doe'],
            'Date': ['2024-12-09', '2024-12-09', '2024-12-10'],
            'Lunch Type': ['Non-Veg', 'Veg', 'Veg'],
            'State': ['confirmed', 'confirmed', 'confirmed'],
            'Remarks': ['', 'Extra spicy', '']
        }
        
        df = pd.DataFrame(sample_data)
        
        # Create Excel file in memory
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Lunch Records', index=False)
            
            # Auto-adjust column widths
            worksheet = writer.sheets['Lunch Records']
            for idx, col in enumerate(df.columns):
                max_length = max(
                    df[col].astype(str).apply(len).max(),
                    len(col)
                ) + 2
                worksheet.column_dimensions[chr(65 + idx)].width = max_length
        
        output.seek(0)
        excel_data = base64.b64encode(output.read())
        
        # Create attachment
        attachment = self.env['ir.attachment'].create({
            'name': 'Lunch_Import_Template.xlsx',
            'type': 'binary',
            'datas': excel_data,
            'mimetype': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        })
        
        return {
            'type': 'ir.actions.act_url',
            'url': f'/web/content/{attachment.id}?download=true',
            'target': 'self',
        }

    def action_back(self):
        """Go back to upload form"""
        self.write({'state': 'draft', 'import_results': False})
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'lunch.excel.import',
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new',
        }