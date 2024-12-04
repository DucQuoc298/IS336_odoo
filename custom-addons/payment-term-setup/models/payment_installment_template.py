from odoo import api, fields, models


class RealEstatePaymentInstallment(models.Model):
    _name = 'real.estate.payment.installment'
    _description = 'Payment Installment'

    installment_code = fields.Char(string="Installment Code", required=True, help="Unique code for the installment")
    ratio = fields.Float(string="Ratio (%)", help="The percentage of the total payment for this installment")
    amount = fields.Float(string="Amount", help="The specific amount for this installment")
    due_date = fields.Date(string="Due Date", help="Due date for this installment")
    time_unit = fields.Selection([
        ('D', 'Day'),
        ('M', 'Month')
    ], string="Time Unit", help="Time unit for the due date (Day or Month)")
    quantity = fields.Integer(string="Quantity", help="Number of time units for the due date")
    description = fields.Text(string="Description", help="Description or additional details for the installment")

    # Relation to Payment Term
    payment_term_id = fields.Many2one(
        comodel_name='real.estate.payment.term',
        string="Payment Term",
        ondelete='cascade',
        help="The payment term associated with this installment"
    )
