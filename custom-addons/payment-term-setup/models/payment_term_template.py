from odoo import api, fields, models
class RealEstatePaymentTerm(models.Model):
    _name = 'real.estate.payment.term'
    _description = 'Payment Term'

    payment_term_code = fields.Char(string="Payment Term Code", required=True, help="Unique code for the payment term")
    name = fields.Char(string="Name", required=True, help="Name of the payment term")
    start_date = fields.Date(string="Start Date", help="Start date of the payment term")
    end_date = fields.Date(string="End Date", help="End date of the payment term")
    is_progressive = fields.Boolean(string="Progressive Payment?", default=False, help="Indicates if the term follows a progressive payment schedule")

    installment_ids = fields.One2many(
        comodel_name='real.estate.payment.installment',
        inverse_name='payment_term_id',
        string="Installments",
        help="Installments under this payment term"
    )
