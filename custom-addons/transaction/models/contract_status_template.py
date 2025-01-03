from odoo import models, fields, api


class RealEstateContractStatus(models.Model):
    _name = 'real.estate.contract.status'
    _description = 'Real Estate Contract Status'

    name = fields.Char(string="Tên trạng thái", required=True)
    contract_status_code = fields.Char(string="Mã trạng thái", required=True)
    description = fields.Text(string="Mô tả")
    property_status_code = fields.Char(string="Mã trạng thái tài sản")
    property_status_id = fields.Many2one(
        comodel_name='real.estate.property.status',
        string="Trạng thái tài sản",
        compute='_compute_property_status',
        inverse="_inverse_property_status",
        store=True
    )
    status = fields.Selection([
        ('C', 'Đã đóng'),
        ('W', 'Đang hoạt động'),
    ], string="Status", required=True, default='W', help="Status of the contract type")
    note = fields.Text(string="Ghi chú")

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