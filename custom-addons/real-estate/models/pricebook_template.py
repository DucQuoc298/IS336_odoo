from odoo import api, fields, models


class RealEstatePriceBook(models.Model):
    _name = 'real.estate.pricebook'
    _description = 'Price book'

    price_book_code = fields.Char(string='Price Book')
    name = fields.Char(string='Price book name')
    # Foreign Key to Account Payment Term
    payment_term_code = fields.Char(
        string="Payment Term Code",
        required=True,
        help="Payment term associated with the pricebook"
    )
    payment_term_id = fields.Many2one(
        comodel_name='account.payment.term',
        compute='_compute_payment_term',
        inverse='_inverse_payment_term',
        string="Payment Term",
        store=True,
    )

    # Foreign Key to Property
    property_code = fields.Char(
        string="Property",
        required=True,
        help="The property associated with this pricebook"
    )
    property_id = fields.Many2one(
        comodel_name='real.estate.property',
        string="Property",
        compute='_compute_property',
        inverse='_inverse_property',
        store=True,
    )

    # Status
    status = fields.Selection([
        ('C', 'Closed'),
        ('W', 'Working'),
    ], string="Status", required=True, default='W', help="Status of the pricebook")

    # Date Range
    start_date = fields.Datetime(string="Start Date", required=True, help="Start date of the pricebook")
    end_date = fields.Datetime(string="End Date", required=True, help="End date of the pricebook")

    notes = fields.Text(string="Notes", help="Additional notes for the pricebook")
    property_value = fields.Float(string="Property Value", required=True, help="Value of the property")
    net_price = fields.Float(string="Net Price", required=True, help="Net price of the property")
    vat_amount = fields.Float(string="VAT Amount",  store=True, help="Calculated VAT amount")
    gross_amount = fields.Float(string="Gross Amount",  store=True, help="Total price including VAT")
    maintenance_price = fields.Float(string="Maintenance Price", required=True, help="Maintenance price for the property")
    land_use_right_value = fields.Float(string="Land Use Right Value", help="Value of the land use rights")

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
