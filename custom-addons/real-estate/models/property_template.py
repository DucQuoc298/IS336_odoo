from odoo import api, fields, models


class RealEstateProperty(models.Model):
    _name = 'real.estate.property'
    _description = 'Property'

    # Fields
    property_name = fields.Char(string="Property", required=True, help="Name of the real estate property")
    status_code = fields.Many2one(
        comodel_name='real.estate.property.status',
        string="Status",
        ondelete='set null',
        help="Current status of the property"
    )
    property_type = fields.Selection([
        ('apartment', 'Apartment'),
        ('land', 'Land'),
        ('villa', 'Villa'),
        ('commercial', 'Commercial'),
    ], string="Property Type", required=True, help="Type of the property")
    block = fields.Char(string="Block", help="Block associated with the property")
    building_code = fields.Many2one(
        comodel_name='real.estate.building',
        string="Building / Land Area",
        help="The building or land area where the property is located"
    )
    total_area = fields.Float(string="Total Area (m²)", help="Total area of the property in square meters")
    property_value = fields.Float(string="Property Value", help="Total value of the property")
    floor_number = fields.Integer(string="Floor Number", help="Floor number for properties within a building")
    usable_area = fields.Float(string="Usable Area (m²)", help="Net usable area of the property")
    unit_price_excl_vat = fields.Float(string="Unit Price (Excl. VAT)", help="Unit price excluding VAT")
    unit_price_incl_vat = fields.Float(string="Unit Price (Incl. VAT)", help="Unit price including VAT")
    vat_taxable_value = fields.Float(string="VAT Taxable Value", help="Value used for VAT calculation")
    land_use_right_value = fields.Float(string="Land Use Right Value", help="Value of the land use rights")
    view = fields.Selection([
        ('sea', 'Sea View'),
        ('garden', 'Garden View'),
        ('city', 'City View'),
        ('mountain', 'Mountain View')
    ], string="View", help="View type of the property")

    @api.model
    def default_get(self, fields_list):
        """Set default values for fields"""
        defaults = super(RealEstateProperty, self).default_get(fields_list)
        return defaults

    def reserve_property(self):
        """Reserve the property by setting its status to 'reserved'."""
        # for record in self:
        #     if record.status == 'available':
        #         record.status = 'reserved'
        #     else:
        #         raise ValueError("Only available properties can be reserved.")
        pass

    def sell_property(self):
        """Sell the property by setting its status to 'sold'."""
        for record in self:
            if record.status in ['available', 'reserved']:
                record.status = 'sold'
            else:
                raise ValueError("Only available or reserved properties can be sold.")

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
