from odoo import models, fields, api


class RealEstateContractStatus(models.Model):
    _name = 'real.estate.contract.status'
    _description = 'Real Estate Contract Status'

    name = fields.Char(string="Contract Status Name", required=True)
    contract_status_code = fields.Char(string="Contract Status Code", required=True)
    description = fields.Text(string="Description")
    property_status_code = fields.Char(string="Property Status Code")
    property_status_id = fields.Many2one(
        comodel_name='real.estate.property.status',
        string="Property Status",
        compute='_compute_property_status',
        inverse="_inverse_property_status",
        store=True
    )
    status = fields.Selection([
        ('C', 'Closed'),
        ('W', 'Working'),
    ], string="Status", required=True, default='W', help="Status of the contract type")
    note = fields.Text(string="Note")

    @api.model
    def default_get(self, fields_list):
        """Set default values for fields"""
        defaults = super(RealEstateContractStatus, self).default_get(fields_list)
        return defaults

    @api.depends('property_status_code')
    def _compute_property_status(self):
        for record in self:
            if record.property_status_code:
                status = self.env['real.estate.property.status'].search([('status_code', '=', record.property_status_code)], limit=1)
                if status:
                    record.property_status_id = status.id
                else:
                    record.property_status_id = False

    def _inverse_property_status(self):
        for record in self:
            if record.property_status_id:
                record.property_status_code = record.property_status_id.status_code
            else:
                record.property_status_code = False