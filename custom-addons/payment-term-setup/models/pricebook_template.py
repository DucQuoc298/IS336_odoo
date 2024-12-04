from odoo import api, fields, models


class RealEstateBuilding(models.Model):
    _name = 'real.estate.building'
    _description = 'Building'

    building_code = fields.Char(string="Block", required=True)  # Block Name/Code
    name = fields.Char(string="Building Name", required=True)  # Building Name
    status = fields.Selection([
        ('planned', 'Planned'),
        ('under_construction', 'Under Construction'),
        ('completed', 'Completed'),
        ('occupied', 'Occupied'),
    ], string="Status", default='planned')  # Current Building Status
    project_code = fields.Many2one(
        comodel_name='real.estate.project',
        string="Project",
        required=True,
        help="The project associated with this building"
    )  # Related Project
    apartment_area = fields.Float(string="Apartment Area (m²)", help="Total apartment area in square meters")  # Apartment Area
    commercial_area = fields.Float(string="Commercial Area (m²)", help="Total commercial area in square meters")  # Commercial Area

    # Optional fields for further details
    total_units = fields.Integer(string="Total Units", help="Number of units in the building")
    description = fields.Text(string="Description", help="Additional notes or description for the building")

    @api.model
    def default_get(self, fields_list):
        """Override default_get to set custom default values."""
        rtn = super(RealEstateBuilding, self).default_get(fields_list)
        rtn['block'] = "Default Block"
        rtn['status'] = 'planned'
        return rtn

    def archive_building(self):
        """Archive the building by updating its status to 'completed'."""
        for record in self:
            record.status = 'completed'

    def duplicate_building(self):
        """Duplicate the building with a slightly modified name."""
        for record in self:
            record.copy({'name': f"{record.name} (Copy)"})

    def unlink_building(self):
        """Delete the building records."""
        for record in self:
            record.unlink()

    def print_building_summary(self):
        """Print a summary of the building records."""
        print(f"Total Buildings: {len(self)}")
        print("Block      Name        Status            Project            Apartment Area (m²)    Commercial Area (m²)")
        for record in self:
            print(f"{record.building_code}      {record.name}      {record.status}      {record.project_code.name}      {record.apartment_area}      {record.commercial_area}")
