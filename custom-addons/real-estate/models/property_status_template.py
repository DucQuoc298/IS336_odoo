from odoo import api, fields, models

class RealEstatePropertyStatus(models.Model):
    _name = 'real.estate.property.status'
    _description = 'Trạng thái tài sản'

    # Fields
    status_code = fields.Char(string="Mã trạng thái", required=True, help="Unique code for the status")
    name = fields.Char(string="Tên", required=True, help="Name of the status")
    is_available = fields.Boolean(string="Is Available?", default=False, help="Indicates if the property is available")
    manages_residents = fields.Boolean(string="Manages Residents?", default=False, help="Indicates if it involves resident management")
    is_rentable = fields.Boolean(string="Is Rentable?", default=False, help="Indicates if the property is available for rent")
    member_ids = fields.One2many('real.estate.property', 'status_code', string='Members', readonly=True)
    # Relations with Property Model
    # property_id = fields.Many2one(
    #     comodel_name='real.estate.property',
    #     string="Property",
    #     ondelete='cascade',
    #     help="The property associated with this status"
    # )

    @api.model
    def create(self, vals):
        """Override create to ensure unique code per property."""
        if 'status_code' in vals and self.search([('status_code', '=', vals['status_code'])]):
            raise ValueError("The code must be unique.")
        return super(RealEstatePropertyStatus, self).create(vals)

    def toggle_availability(self):
        """Toggle the availability status."""
        for record in self:
            record.is_available = not record.is_available

    def unlink(self):
        """Override unlink to prevent deletion of essential statuses."""
        for record in self:
            if not record.is_rentable and not record.is_available:
                raise ValueError("This status is essential and cannot be deleted.")
        return super(RealEstatePropertyStatus, self).unlink()