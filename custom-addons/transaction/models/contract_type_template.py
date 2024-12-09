from odoo import models, fields, api


class RealEstateContractType(models.Model):
    _name = 'real.estate.contract.type'
    _description = 'Real Estate Contract Type'

    name = fields.Char(string="Contract Type Name", required=True)
    contract_type_code = fields.Char(string="Contract Type Code", required=True)
    description = fields.Text(string="Description")
    status = fields.Selection([
        ('C', 'Closed'),
        ('W', 'Working'),
    ], string="Status", required=True, default='W', help="Status of the contract type")
    note = fields.Text(string="Note")
    contract_sequence = fields.Selection([('N', 'N')],
                                         string="Contract Sequence")
    revenue_type = fields.Selection([('N', 'N')],string="Revenue Type")
    @api.model
    def default_get(self, fields_list):
        """Set default values for fields"""
        defaults = super(RealEstateContractType, self).default_get(fields_list)
        return defaults
