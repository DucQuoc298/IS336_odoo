from odoo import models, fields, api
from odoo.exceptions import ValidationError


class RealEstateContract(models.Model):
    _name = 'real.estate.contract'
    _description = 'Real Estate Contract'
    _order = 'id desc'

    contract_code = fields.Char(string="Mã hợp đồng", required=True)
    description = fields.Text(string="Mô tả")
    contract_type_code = fields.Char(string="Mã loại hợp đồng")
    contract_type_id = fields.Many2one(
        comodel_name='real.estate.contract.type',
        string="Loại hợp đồng",
        compute='_compute_contract_type',
        inverse="_inverse_contract_type",
        store=True
    )
    contract_status_code = fields.Char(string="Mã tình trạng giao dịch", required=True)
    contract_status_id = fields.Many2one(
        comodel_name='real.estate.contract.status',
        string="Trạng thái giao dịch",
        compute='_compute_contract_status',
        inverse="_inverse_contract_status",
        store=True
    )
    property_code = fields.Char(string="Mã tài sản", required=True)
    property_id = fields.Many2one(
        comodel_name='real.estate.property',
        string="Tài sản",
        compute='_compute_property',
        inverse="_inverse_property",
        store=True
    )
    property_number = fields.Char(string="Số tài sản")
    client_code = fields.Char(string="Mã khách hàng")
    contact_id = fields.Many2one(
        comodel_name='res.partner',
        string="Khách hàng",
        compute='_compute_contact',
        inverse="_inverse_contact",
        store=True
    )
    pricebook_code = fields.Char(string="Mã bảng giá")
    pricebook_id = fields.Many2one(
        comodel_name='real.estate.pricebook',
        string="Bảng giá",
        compute='_compute_pricebook',
        inverse="_inverse_pricebook",
        store=True
    )
    payment_term_code = fields.Char(string="Mã phương thức thanh toán")
    payment_term_id = fields.Many2one(
        comodel_name='account.payment.term',
        string="Phương thức thanh toán",
        compute='_compute_payment_term',
        inverse="_inverse_payment_term",
        store=True
    )
    contract_value = fields.Float(string="Giá trị hợp đồng", required=True, default=0.0)
    net_price = fields.Float(string="Giá chưa có VAT", required=True, help="Net price of the property", default=0.0)
    vat_amount = fields.Float(string="Thuế VAT", required=True, help="Calculated VAT amount", default=0.0)
    gross_amount = fields.Float(string="Giá để tính VAT", required=True, help="Total price including VAT", default=0.0)
    maintenance_price = fields.Float(string="Chi phí bảo trì", required=True,
                                     help="Maintenance price for the property", default=0.0)
    land_use_right_value = fields.Float(string="Giá sử dụng đất", help="Value of the land use rights", default=0.0)
    deposit_value = fields.Float(string="Giá cọc", required=True, help="Value of the deposit", default=0.0)
    other_fee_value = fields.Float(string="Chi phí khác", help="Value of the other fee value")
    start_date = fields.Datetime(string="Ngày bắt đầu")
    effective_date = fields.Datetime(string="Ngày có hiệu lực")
    end_date = fields.Datetime(string="Ngày kết thúc")
    notes = fields.Text(string="Ghi chú")
    order_id = fields.Many2one(
        comodel_name='real.estate.order',
        string="Đơn hàng",
        help="The booking associated with this contract",
    )
    invoice_ids = fields.One2many(
        comodel_name='account.move',
        inverse_name='contract_id',
        string="Hoá đơn",
        copy=False
    )

    invoice_count = fields.Integer(
        string="Số hoá đơn",
        compute="_compute_invoice_count",
        store=True,
    )
    def action_view_invoice(self, invoices=False):
        if not invoices:
            invoices = self.mapped('invoice_ids')
        action = self.env['ir.actions.actions']._for_xml_id('account.action_move_out_invoice_type')
        if len(invoices) > 1:
            action['domain'] = [('id', 'in', invoices.ids)]
        elif len(invoices) == 1:
            form_view = [(self.env.ref('account.view_move_form').id, 'form')]
            if 'views' in action:
                action['views'] = form_view + [(state,view) for state,view in action['views'] if view != 'form']
            else:
                action['views'] = form_view
            action['res_id'] = invoices.id
        else:
            action = {'type': 'ir.actions.act_window_close'}

        context = {
            'default_move_type': 'out_invoice',
        }
        if len(self) == 1:
            context.update({
                'default_partner_id': self.contact_id.id,
                # 'default_partner_shipping_id': self.partner_shipping_id.id,
                'default_invoice_payment_term_id': self.payment_term_id.id or self.env['account.move'].default_get(['invoice_payment_term_id']).get('invoice_payment_term_id'),
                'default_invoice_origin': self.contract_code,
            })
        action['context'] = context
        return action

    @api.onchange('pricebook_id')
    def _onchange_pricebook_id(self):
        if self.pricebook_id:
            self.net_price = self.pricebook_id.net_price
            self.gross_amount = self.pricebook_id.gross_amount
            self.maintenance_price = self.pricebook_id.maintenance_price
            self.land_use_right_value = self.pricebook_id.land_use_right_value
            self.vat_amount = self.pricebook_id.vat_amount
            self.contract_value = self.pricebook_id.vat_amount + self.pricebook_id.net_price

    @api.onchange('vat_amount')
    def _onchange_vat_amount(self):
        if self.vat_amount:
            self.contract_value = self.vat_amount + self.net_price

    @api.onchange('net_price')
    def _onchange_net_price(self):
        if self.net_price:
            self.contract_value = self.vat_amount + self.net_price

    @api.onchange('gross_amount')
    def _onchange_gross_amount(self):
        if self.gross_amount:
            self.vat_amount = self.gross_amount * 0.1

    @api.onchange('order_id')
    def _onchange_order_id(self):
        if self.order_id:
            self.deposit_value = self.order_id.order_value

    @api.depends('invoice_ids')
    def _compute_invoice_count(self):
        for record in self:
            record.invoice_count = len(record.invoice_ids)

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

    def action_create_invoice(self):
        for contract in self:
            invoice_vals = {
                'partner_id': contract.contact_id.id,
                'move_type': 'out_invoice',
                'invoice_date': fields.Date.today(),
                'invoice_origin': contract.contract_code,
                'invoice_line_ids': [(0, 0, {
                    'name': f"Property: {contract.property_id.property_name}",
                    'quantity': 1.0,
                    'price_unit': contract.contract_value,

                })],

                'invoice_currency_rate': 0.1,
                'contract_id': contract.id,
                'invoice_payment_term_id': contract.payment_term_id.id,
            }
            invoice = self.env['account.move'].create(invoice_vals)
            contract.invoice_ids = [(4, invoice.id)]
            return {
                'type': 'ir.actions.act_window',
                'name': 'Invoice',
                'view_mode': 'form',
                'res_model': 'account.move',
                'res_id': invoice.id,
            }


    def action_liquidation_deposit(self, vals=None):
        tlhdc_status = self.env['real.estate.contract.status'].search([('contract_status_code', '=', 'TLYHDC')], limit=1)
        if not tlhdc_status:
            raise ValueError("Trạng thái 'Đặt Cọc' chưa được thiết lập trong hệ thống.")

        for record in self:
            record.contract_status_id = tlhdc_status.id
            contract_vals = {
                'property_id': record.property_id.id,
                'contact_id': record.contact_id.id,
                'contract_value': record.contract_value,
                'order_id': record.order_id.id,
                'contract_status_code': 'HDO',
                'contract_type_id': record.contract_type_id.id,
                'property_code': record.property_code,
                'net_price':  record.net_price,
                'vat_amount': record.vat_amount,
                'gross_amount': record.gross_amount,
                'maintenance_price': record.maintenance_price,
                'land_use_right_value': record.land_use_right_value,
                'deposit_value': record.deposit_value,
                'other_fee_value': record.other_fee_value,
                'start_date': record.start_date,
                'effective_date': record.effective_date,
                'end_date': record.end_date,
                'notes': record.notes,
                'payment_term_id': record.payment_term_id.id,
                'pricebook_id': record.pricebook_id.id,
            }
            # if record.pricebook_id:
            #     contract_vals['pricebook_id'] = record.pricebook_id.id
            new_contract = self.create(contract_vals)
            return {
                'type': 'ir.actions.act_window',
                'name': 'Contract',
                'view_mode': 'form',
                'res_model': 'real.estate.contract',
                'res_id': new_contract.id,
            }
        return True

    def action_liquidation(self):
        tlhdo_status = self.env['real.estate.contract.status'].search([('contract_status_code', '=', 'TLYHDO')], limit=1)
        if not tlhdo_status:
            raise ValueError("Trạng thái 'Đặt Cọc' chưa được thiết lập trong hệ thống.")
        self.contract_status_id = tlhdo_status.id

    def terminate_contract(self):
        cduhdo_status = self.env['real.estate.contract.status'].search([('contract_status_code', '=', 'CDUHDO')], limit=1)
        if not cduhdo_status:
            raise ValueError("Trạng thái 'Đặt Cọc' chưa được thiết lập trong hệ thống.")
        self.contract_status_id = cduhdo_status.id

    def approve_sale_contract(self):
        hdo_status = self.env['real.estate.contract.status'].search([('contract_status_code', '=', 'HDO')], limit=1)
        if not hdo_status:
            raise ValueError("Trạng thái 'Đặt Cọc' chưa được thiết lập trong hệ thống.")
        self.contract_status_id = hdo_status.id
    def approve_deposit_contract(self):
        hdc_status = self.env['real.estate.contract.status'].search([('contract_status_code', '=', 'HDC')], limit=1)
        if not hdc_status:
            raise ValueError("Trạng thái 'Đặt Cọc' chưa được thiết lập trong hệ thống.")
        self.contract_status_id = hdc_status.id

    def action_hand_over_property(self):
        if self.property_id.status_code != 'BGI':
            raise ValidationError(
                f"Không thể cập nhật bàn giao vì sản phẩm '{self.property_id.property_name}' chưa ở trạng thái 'Bàn giao sản phẩm'.")
        bgi_status = self.env['real.estate.contract.status'].search([('contract_status_code', '=', 'BGI')], limit=1)
        if not bgi_status:
            raise ValueError("Trạng thái 'Bàn giao sản phẩm' chưa được thiết lập trong hệ thống.")

        self.contract_status_id = bgi_status.id
        return True

    def action_hand_over_book(self):
        if self.property_id.status_code != 'BGI':
            raise ValidationError(
                f"Không thể cập nhật bàn giao vì sản phẩm '{self.property_id.property_name}' chưa ở trạng thái 'Bàn giao sổ'.")
        bgi_status = self.env['real.estate.contract.status'].search([('contract_status_code', '=', 'BGS')], limit=1)
        if not bgi_status:
            raise ValueError("Trạng thái 'Bàn giao sổ' chưa được thiết lập trong hệ thống.")

        self.contract_status_id = bgi_status.id
        return True

    def action_cancel(self):
        huy_status = self.env['real.estate.contract.status'].search([('contract_status_code', '=', 'TLYHUY')], limit=1)
        if not huy_status:
            raise ValueError("Trạng thái 'Huỷ' chưa được thiết lập trong hệ thống.")
        self.contract_status_id = huy_status.id
        return True
    def action_liquidation_cancel_deposit(self):
        tlydcohc_status = self.env['real.estate.contract.status'].search([('contract_status_code', '=', 'TLYDCOHC')], limit=1)
        if not tlydcohc_status:
            raise ValueError("Trạng thái 'Thanh Lý huỷ cọc' chưa được thiết lập trong hệ thống.")
        self.contract_status_id = tlydcohc_status.id
        for contract in self:
            invoice_vals = {
                'partner_id': contract.contact_id.id,
                'move_type': 'out_refund',
                'invoice_date': fields.Date.today(),
                'invoice_origin': contract.contract_code,
                'invoice_line_ids': [(0, 0, {
                    'name': f"Thanh lý trả cọc: {contract.property_id.property_name}",
                    'quantity': 1.0,
                    'price_unit': contract.net_price,
                    'tax_ids': [(6, 0, [1])],
                })],
                'contract_id': contract.id,
                'invoice_payment_term_id': contract.payment_term_id.id,
            }
            invoice = self.env['account.move'].create(invoice_vals)
            contract.invoice_ids = [(4, invoice.id)]
            return {
                'type': 'ir.actions.act_window',
                'name': 'Invoice',
                'view_mode': 'form',
                'res_model': 'account.move',
                'res_id': invoice.id,
            }