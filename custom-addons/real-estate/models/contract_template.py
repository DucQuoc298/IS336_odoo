from odoo import models, fields, api


class RealEstateContract(models.Model):
    _name = 'real.estate.contract'
    _description = 'Real Estate Contract'

    contract_code = fields.Char(string="Contract Code", required=True)
    description = fields.Text(string="Description")
    contract_type_code = fields.Char(string="Contract Type Code")
    contract_type_id = fields.Many2one(
        comodel_name='real.estate.contract.type',
        string="Contract Type",
        compute='_compute_contract_type',
        inverse="_inverse_contract_type",
        store=True
    )
    contract_status_code = fields.Char(string="Contract Status Code", required=True)
    contract_status_id = fields.Many2one(
        comodel_name='real.estate.contract.status',
        string="Contract Status",
        compute='_compute_contract_status',
        inverse="_inverse_contract_status",
        store=True
    )
    property_code = fields.Char(string="Property Code", required=True)
    property_id = fields.Many2one(
        comodel_name='real.estate.property',
        string="Property",
        compute='_compute_property',
        inverse="_inverse_property",
        store=True
    )
    property_number = fields.Char(string="Property Number")
    client_code = fields.Char(string="Client Code")
    contact_id = fields.Many2one(
        comodel_name='res.partner',
        string="Client",
        compute='_compute_contact',
        inverse="_inverse_contact",
        store=True
    )
    pricebook_code = fields.Char(string="Price Book Code")
    pricebook_id = fields.Many2one(
        comodel_name='real.estate.pricebook',
        string="Price Book",
        compute='_compute_pricebook',
        inverse="_inverse_pricebook",
        store=True
    )
    payment_term_code = fields.Char(string="Payment Term Code")
    payment_term_id = fields.Many2one(
        comodel_name='account.payment.term',
        string="Payment Term",
        compute='_compute_payment_term',
        inverse="_inverse_ payment_term",
        store=True
    )
    contract_value = fields.Float(string="Contract Value", required=True, default=0.0)
    net_price = fields.Float(string="Net Price", required=True, help="Net price of the property", default=0.0)
    vat_amount = fields.Float(string="VAT Amount", required=True, help="Calculated VAT amount", default=0.0)
    gross_amount = fields.Float(string="Gross Amount", required=True, help="Total price including VAT", default=0.0)
    maintenance_price = fields.Float(string="Maintenance Price", required=True,
                                     help="Maintenance price for the property", default=0.0)
    land_use_right_value = fields.Float(string="Land Use Right Value", help="Value of the land use rights", default=0.0)
    deposit_value = fields.Float(string="Deposit Value", required=True, help="Value of the deposit", default=0.0)
    other_fee_value = fields.Float(string="Other Fee Value", help="Value of the other fee value")
    start_date = fields.Datetime(string="Start Date")
    effective_date = fields.Datetime(string="Effective Date")
    end_date = fields.Datetime(string="End Date")
    notes = fields.Text(string="Notes")
    order_id = fields.Many2one(
        comodel_name='real.estate.order',
        string="Order",
        help="The booking associated with this contract",
    )

    @api.model
    def default_get(self, fields_list):
        """Set default values for fields"""
        defaults = super(RealEstateContract, self).default_get(fields_list)
        return defaults

    @api.depends('contract_status_code')
    def _compute_contract_status(self):
        for record in self:
            if record.contract_status_code:
                status = self.env['real.estate.contract.status'].search([('contract_status_code', '=', record.contract_status_code)], limit=1)
                if status:
                    record.contract_status_id = status.id
                else:
                    record.contract_status_id = False

    def _inverse_contract_status(self):
        for record in self:
            if record.contract_status_id:
                record.contract_status_code = record.contract_status_id.contract_status_code
            else:
                record.contract_status_code = False

    @api.depends('contract_type_code')
    def _compute_contract_type(self):
        for record in self:
            if record.contract_type_code:
                type = self.env['real.estate.contract.type'].search(
                    [('contract_type_code', '=', record.contract_type_code)], limit=1)
                if type:
                    record.contract_type_id = type.id
                else:
                    record.contract_type_id = False

    def _inverse_contract_type(self):
        for record in self:
            if record.contract_type_id:
                record.contract_type_code = record.contract_type_id.contract_type_code
            else:
                record.contract_type_code = False

    @api.depends('property_code')
    def _compute_property(self):
        for record in self:
            if record.property_code:
                property = self.env['real.estate.property'].search(
                    [('property', '=', record.property_code)], limit=1)
                if property:
                    record.property_id = property.id
                else:
                    record.property_id = False

    def _inverse_property(self):
        for record in self:
            if record.property_id:
                record.property_code = record.property_id.property
            else:
                record.property_code = False

    @api.depends('client_code')
    def _compute_contact(self):
        for record in self:
            if record.client_code:
                contact = self.env['res.partner'].search(
                    [('contact_code', '=', record.client_code)], limit=1)
                if contact:
                    record.contact_id = contact.id
                else:
                    record.contact_id = False

    def _inverse_contact(self):
        for record in self:
            if record.contact_id:
                record.client_code = record.contact_id.contact_code
            else:
                record.client_code = False

    @api.depends('pricebook_code')
    def _compute_pricebook(self):
        for record in self:
            if record.pricebook_code:
                pricebook = self.env['real.estate.pricebook'].search(
                    [('price_book_code', '=', record.pricebook_code)], limit=1)
                if pricebook:
                    record.pricebook_id = pricebook.id
                else:
                    record.pricebook_id = False

    def _inverse_pricebook(self):
        for record in self:
            if record.pricebook_id:
                record.pricebook_code = record.pricebook_id.price_book_code
            else:
                record.pricebook_code = False

    @api.depends('payment_term_code')
    def _compute_payment_term(self):
        for record in self:
            if record.payment_term_code:
                payment_term = self.env['account.payment.term'].search(
                    [('payment_term_code', '=', record.payment_term_code)], limit=1)
                if payment_term:
                    record.payment_term_id = payment_term.id
                else:
                    record.payment_term_id = False

    def _inverse_payment_term(self):
        for record in self:
            if record.payment_term_id:
                record.payment_term_code = record.payment_term_id.payment_term_code
            else:
                record.payment_term_code = False

    @api.depends('contract_code')
    def _compute_display_name(self):
        for contract in self:
            contract.display_name = contract.contract_code

    def create(self, vals):
        last_contract = self.env['real.estate.contract'].search([], order='id desc', limit=1)
        if last_contract and last_contract.contract_code:
            next_code_number = last_contract.id + 1
        else:
            next_code_number = 1
        vals['contract_code'] = f"C{next_code_number:05d}"
        return super(RealEstateContract, self).create(vals)