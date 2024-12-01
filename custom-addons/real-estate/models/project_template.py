# -*- coding: utf-8 -*-
from odoo import api, fields, models
from odoo.exceptions import UserError
from lxml import etree


class RealEstateProject(models.Model):
    _name = 'real.estate.project'
    _description = 'Project'

    project_code = fields.Char(string="Project", required=True)  # Project Code
    name = fields.Char(string="Name", required=True)  # Project Name
    status = fields.Selection([
        ('pending', 'Pending'),
        ('ongoing', 'Ongoing'),
        ('completed', 'Completed')
    ], string="Status", default='pending')  # Project Status
    project_type = fields.Selection([
        ('residential', 'Residential'),
        ('commercial', 'Commercial'),
        ('mixed_use', 'Mixed-Use')
    ], string="Project Type", required=True)  # Project Type
    deposit_value = fields.Float(string="Deposit Value")  # Deposit Value
    estimated_handover_date = fields.Date(string="Expected Delivery Month")  # Estimated Handover Date
    apartment_area = fields.Float(string="Area (m²)")  # Apartment Area

    total_units = fields.Integer(string="Total Units")  # Total Units
    location = fields.Char(string="Location")  # Location
    description = fields.Text(string="Description")

    @api.model
    def default_get(self, fields_list):
        """Set default values for fields"""
        defaults = super(RealEstateProject, self).default_get(fields_list)
        return defaults
