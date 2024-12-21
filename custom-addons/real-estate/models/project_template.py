# -*- coding: utf-8 -*-
from pygments.lexer import default

from odoo import api, fields, models
from odoo.exceptions import UserError
from datetime import date
from lxml import etree


class RealEstateProject(models.Model):
    _name = 'real.estate.project'
    _description = 'Project'

    project_code = fields.Char(string="Dự án", required=True)
    name = fields.Char(string="Tên", required=True)
    status = fields.Selection([
        ('C', 'Đã đóng'),
        ('W', 'Đang hoạt động')
    ], string="Status", default='W')
    project_type = fields.Selection([
        ('DTMG', 'Dự án đầu tư môi giới'),
        ('DTTC', 'Dự án đầu tư công ty con'),
        ('DTTT', 'Dự án trực tiếp đầu tư'),
        ('MGTH', 'Dự án môi giới (Không thu đợt thanh toán)'),
    ], string="Loại dự án", required=True, default='DTMG')
    value = fields.Float(string="Giá trị dự án")
    estimated_handover_date = fields.Date(string="Ngày bàn giao", default=date(1991, 1, 1))
    apartment_area = fields.Float(string="Diện tích (m²)")

    total_units = fields.Integer(string="Số lượng sản phẩm")
    location = fields.Char(string="Địa chỉ")
    description = fields.Text(string="Mô tả")

    @api.model
    def default_get(self, fields_list):
        """Set default values for fields"""
        defaults = super(RealEstateProject, self).default_get(fields_list)
        return defaults
