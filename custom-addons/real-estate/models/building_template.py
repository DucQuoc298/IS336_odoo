from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class RealEstateBuilding(models.Model):
    _name = 'real.estate.building'
    _description = 'Building'

    building_code = fields.Char(string="Building", required=True)
    name = fields.Char(string="Name", required=True)
    status = fields.Selection([
        ('W', 'Working'),
        ('C', 'Closed')
    ], string="Status", default='W')
    project_code = fields.Many2one(
        'real.estate.project',
        string="Project Code",
        required=True,
        help="The project associated with this building"
    )
    project_id = fields.Many2one(
        'real.estate.project',
         string="Project",
         # compute="_compute_project",
         store=True
    )
    address = fields.Char(string="Address")
    apartment_area = fields.Float(string="Apartment Area (m²)", help="Total apartment area in square meters")
    commercial_area = fields.Float(string="Commercial Area (m²)", help="Total commercial area in square meters")

    total_units = fields.Integer(string="Total Units", help="Number of units in the building")
    description = fields.Text(string="Description", help="Additional notes or description for the building")

    # @api.depends('project_code')
    # def _compute_project(self):
    #     for record in self:
    #         if record.project_code:
    #             # Tìm kiếm dự án dựa trên project_code
    #             project = self.env['real.estate.project'].search([('project_code', '=', record.project_code)], limit=1)
    #             if project:
    #                 record.project_id = project.id
    #             else:
    #                 record.project_id = False
    @api.model
    def create(self, vals):
        if 'project_code' in vals and not isinstance(vals['project_code'], int):
            project = self.env['real.estate.project'].search([('project_code', '=', vals['project_code'])], limit=1)
            if not project:
                raise ValidationError(_("Project with code '%s' does not exist." % vals['project_code']))
            vals['project_code'] = project.id
        return super(RealEstateBuilding, self).create(vals)
    def default_get(self, fields_list):
        """Set default values for fields"""
        defaults = super(RealEstateBuilding, self).default_get(fields_list)
        return defaults