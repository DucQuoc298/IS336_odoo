import base64
from odoo import api, fields, models, tools
from odoo.fields import Properties


class RealEstateProperty(models.Model):
    _name = 'real.estate.property'
    _description = 'Tài sản'
    _order = "is_favorite desc"
    _rec_name = 'property_name'

    property = fields.Char('Mã tài sản', required=True)
    property_name = fields.Char(string="Tên tài sản", required=True, help="Name of the real estate property", default="")
    status_code = fields.Char(
        string="Mã trạng thái tài sản",
        required=True,
        help="The project associated with this building"
    )
    status_id = fields.Many2one(
        comodel_name='real.estate.property.status',
        string="Trạng thái tài sản",
        compute='_compute_status',
        inverse="_inverse_status",
        store=True
    )
    description = fields.Char(string="Mô tả", help="Description of the property")
    property_type = fields.Selection([
        ('apartment', 'Khu dân cư'),
        ('land', 'Đất'),
        ('villa', 'Villa'),
        ('commercial', 'Khu thương mại'),
    ], string="Loại tài sản",default='apartment', help="Type of the property")
    building_code = fields.Char(string="Mã toà nhà", help="Building associated with the property")
    building_id = fields.Many2one(
        comodel_name='real.estate.building',
        string="Toà nhà",
        compute='_compute_building',
        inverse="_inverse_building",
        store=True
    )
    is_favorite = fields.Boolean(string="Favorite")
    total_area = fields.Float(string="Tổng diện tích (m²)", help="Total area of the property in square meters")
    property_value = fields.Float(string="Giá trị tài sản", help="Total value of the property")
    floor = fields.Char(string="Tầng", help="Floor number for properties within a building")
    usable_area = fields.Float(string="Diện tích có thể sử dụng (m²)", help="Net usable area of the property")
    unit_price_excl_vat = fields.Float(string="Giá (không có VAT)", help="Unit price excluding VAT")
    unit_price_incl_vat = fields.Float(string="Giá (Có VAT)", help="Unit price including VAT")
    vat_taxable_value = fields.Float(string="Giá trị VAT", help="Value used for VAT calculation")
    land_use_right_value = fields.Float(string="Giá trị sử dụng đất", help="Value of the land use rights")
    view = fields.Selection([
        ('sea', 'Cảnh biển'),
        ('garden', 'Cảnh vườn'),
        ('city', 'Cảnh thành phố'),
        ('mountain', 'Cảnh Đồi núi')
    ], string="Phong cảnh", help="View type of the property")
    width = fields.Float(string="Rộng", help="Width of the property")
    length = fields.Float(string="Dài", help="Length of the property")
    bedroom = fields.Float(string="Phòng ngủ", help="Bedroom of the property")
    image = fields.Binary(string="Hình ảnh", attachment=True)

    @api.depends('status_code')
    def _compute_status(self):
        for record in self:
            if record.status_code:
                status = self.env['real.estate.property.status'].search([('status_code', '=', record.status_code)], limit=1)
                if status:
                    record.status_id = status.id
                else:
                    record.status_id = False

    def _inverse_status(self):
        for record in self:
            if record.status_id:
                record.status_code = record.status_id.status_code
            else:
                record.status_code = False
    @api.depends('building_code')
    def _compute_building(self):
        for record in self:
            if record.building_code:
                building = self.env['real.estate.building'].search([('building_code', '=', record.building_code)], limit=1)
                if building:
                    record.building_id = building.id
                else:
                    record.building_id = False
    def _inverse_building(self):
        for record in self:
            if record.building_id:
                record.building_code = record.building_id.building_code
            else:
                record.building_code = False

    @api.depends('property_name')
    def _compute_display_name(self):
        for property in self:
            property.display_name =  property.property_name
    @api.model
    def default_get(self, fields_list):
        """Set default values for fields"""
        defaults = super(RealEstateProperty, self).default_get(fields_list)
        return defaults
    def compute_vat_prices(self):
        """Calculate VAT-inclusive and VAT-taxable values."""
        for record in self:
            vat_rate = 0.1  # Example VAT rate of 10%
            record.unit_price_incl_vat = record.unit_price_excl_vat * (1 + vat_rate)
            record.vat_taxable_value = record.unit_price_excl_vat * vat_rate

    def set_status(self, status_code):
        """Set the status of the property based on the status code."""
        status = self.env['real.estate.property.status'].search([('status_code', '=', status_code)], limit=1)
        if not status:
            raise ValueError(f"Status with code '{status_code}' does not exist.")
        self.status_code = status_code

    def unlink(self):
        """Override unlink to prevent deletion of sold properties."""
        for record in self:
            if record.status_code == 'sold':
                raise ValueError("Sold properties cannot be deleted.")
        return super(RealEstateProperty, self).unlink()
