from odoo import api, fields, models


class RealEstatePriceBook(models.Model):
    _name = 'real.estate.pricebook'
    _description = 'Pricebook'

    # Foreign Key to Account Payment Term
    payment_term_id = fields.Many2one(
        comodel_name='account.payment.term',
        string="Payment Term",
        required=True,
        help="Payment term associated with the pricebook"
    )

    # Foreign Key to Property
    property_id = fields.Many2one(
        comodel_name='real.estate.property',
        string="Property",
        required=True,
        help="The property associated with this pricebook"
    )

    # Status
    status = fields.Selection([
        ('C', 'Closed'),
        ('W', 'Working'),
    ], string="Status", required=True, default='W', help="Status of the pricebook")

    # Date Range
    start_date = fields.Date(string="Start Date", required=True, help="Start date of the pricebook")
    end_date = fields.Date(string="End Date", required=True, help="End date of the pricebook")

    # Notes
    notes = fields.Text(string="Notes", help="Additional notes for the pricebook")

    # Price Details
    net_price = fields.Float(string="Net Price", required=True, help="Net price of the property")
    vat_amount = fields.Float(string="VAT Amount", compute='_compute_vat_amount', store=True, help="Calculated VAT amount")
    gross_amount = fields.Float(string="Gross Amount", compute='_compute_gross_amount', store=True, help="Total price including VAT")
    maintenance_price = fields.Float(string="Maintenance Price", required=True, help="Maintenance price for the property")
    land_use_right_value = fields.Float(string="Land Use Right Value", help="Value of the land use rights")

    # Computed Fields
    @api.depends('net_price')
    def _compute_vat_amount(self):
        """Compute the VAT amount based on net price."""
        for record in self:
            vat_rate = 0.1  # Example VAT rate of 10%
            record.vat_amount = record.net_price * vat_rate

    @api.depends('net_price', 'vat_amount')
    def _compute_gross_amount(self):
        """Compute the gross amount (Net Price + VAT)."""
        for record in self:
            record.gross_amount = record.net_price + record.vat_amount
