from odoo import api, fields, models


class RealEstatePriceBook(models.Model):
    _name = 'real.estate.pricebook'
    _description = 'Bảng giá'

    price_book_code = fields.Char(string='Mã bảng giá')
    name = fields.Char(string='Tên bảng giá')
    # Foreign Key to Account Payment Term
    payment_term_code = fields.Char(
        string="Mã phương thức thanh toán",
        required=True,
        help="Payment term associated with the pricebook"
    )
    payment_term_id = fields.Many2one(
        comodel_name='account.payment.term',
        compute='_compute_payment_term',
        inverse='_inverse_payment_term',
        string="Phương thức thanh toán",
        store=True,
    )

    # Foreign Key to Property
    property_code = fields.Char(
        string="Tài sản",
        required=True,
        help="The property associated with this pricebook"
    )
    property_id = fields.Many2one(
        comodel_name='real.estate.property',
        string="Tài sản",
        compute='_compute_property',
        inverse='_inverse_property',
        store=True,
    )

    # Status
    status = fields.Selection([
        ('C', 'Đã đóng'),
        ('W', 'Đang hoạt động'),
    ], string="Trạng thái", required=True, default='W', help="Status of the pricebook")

    # Date Range
    start_date = fields.Datetime(string="Ngày bắt đầu", required=True, help="Start date of the pricebook")
    end_date = fields.Datetime(string="Ngày kết thúc", required=True, help="End date of the pricebook")

    notes = fields.Text(string="Ghi chú", help="Additional notes for the pricebook")
    property_value = fields.Float(string="Giá trị tài sản", related='property_id.property_value',  required=True, help="Value of the property")
    net_price = fields.Float(string="Giá cơ bản", required=True, help="Net price of the property")
    vat_amount = fields.Float(string="Thuế VAT",  store=True, help="Calculated VAT amount")
    gross_amount = fields.Float(string="Giá tính thuế VAT",  store=True, help="Total price including VAT")
    maintenance_price = fields.Float(string="Giá bảo trì", required=True, help="Maintenance price for the property")
    land_use_right_value = fields.Float(string="Giá sử dụng đất", help="Value of the land use rights")

    # Computed Fields
    @api.depends('net_price')
    def _compute_vat_amount(self):
        """Compute the VAT amount based on net price."""
        for record in self:
            vat_rate = 0.1  # Example VAT rate of 10%
            record.vat_amount = record.gross_amount * vat_rate

    @api.depends('payment_term_code')
    def _compute_payment_term(self):
        for record in self:
            if record.payment_term_code:
                payment_term = self.env['account.payment.term'].search([('payment_term_code', '=', record.payment_term_code)],
                                                                   limit=1)
                if payment_term:
                    record.payment_term_id = payment_term.id
                else:
                    record.payment_term_id = False
    def _inverse_payment_term(self):
        for record in self:
            if record.payment_term_id:
                record.payment_term_code = record.payment_term_id.building_code
            else:
                record.payment_term_code = False
    @api.depends('property_code')
    def _compute_property(self):
        for record in self:
            if record.property_code:
                property = self.env['real.estate.property'].search(
                    [('property', '=', record.property_code)],
                    limit=1)
                if property:
                    record.property_id = property.id
                else:
                    record.property_id = False

    def _inverse_property(self):
        for record in self:
            if record.property_id:
                record.property_code = record.property_id.property_code
            else:
                record.property_code = False
