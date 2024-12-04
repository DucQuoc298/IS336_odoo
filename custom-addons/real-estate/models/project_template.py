# -*- coding: utf-8 -*-
from pygments.lexer import default

from odoo import api, fields, models
from odoo.exceptions import UserError
from datetime import date
from lxml import etree


class RealEstateProject(models.Model):
    _name = 'real.estate.project'
    _description = 'Project'

    project_code = fields.Char(string="Project", required=True)
    name = fields.Char(string="Name", required=True)
    status = fields.Selection([
        ('C', 'Closed'),
        ('W', 'Working')
    ], string="Status", default='W')
    project_type = fields.Selection([
        ('DTMG', 'Brokerage investment project'),
        ('DTTC', 'Subsidiary investment project'),
        ('DTTT', 'Direct investment project'),
        ('MGTH', 'Brokerage project (no payment collection)'),
    ], string="Project Type", required=True, default='DTMG')
    deposit_value = fields.Float(string="Deposit Value")  # Deposit Value
    estimated_handover_date = fields.Date(string="Expected Delivery Month", default=date(1991, 1, 1))
    apartment_area = fields.Float(string="Area (m²)")

    total_units = fields.Integer(string="Total Units")
    location = fields.Char(string="Location")
    description = fields.Text(string="Description")

    @api.model
    def default_get(self, fields_list):
        """Set default values for fields"""
        defaults = super(RealEstateProject, self).default_get(fields_list)
        return defaults
