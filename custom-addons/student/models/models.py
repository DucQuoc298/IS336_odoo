from odoo import fields, models

class Student(models.Model):
    _name = 'wb.student'
    _description = 'This is student profile'

    name = fields.Char(string='Name')