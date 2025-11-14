from odoo import models, fields

class LunchTypes(models.Model):
    _name = 'lunch.types'
    _description = 'Employee Lunch Types'
    _rec_name = 'lunch_type' 
    
    lunch_type = fields.Char(string='Lunch Type', required=True)
    cost = fields.Float(string='Cost', required=True)
    note = fields.Text(string='Remarks')