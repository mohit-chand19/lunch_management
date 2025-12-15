from odoo import models, fields

class LunchTiming(models.Model):
    _name = 'lunch.timing'
    _description = 'Lunch Time Configuration'
    _rec_name = 'start_time'

    start_time = fields.Float(string="Start Time (Hours)", required=True)
    end_time = fields.Float(string="End Time (Hours)", required=True)
    note = fields.Text(string="Remarks")
