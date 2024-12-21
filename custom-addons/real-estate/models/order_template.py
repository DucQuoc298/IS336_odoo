import base64
from odoo import api, fields, models, tools
from odoo.exceptions import UserError, ValidationError
from odoo.fields import Properties, Datetime

SALE_ORDER_STATE = [
    ('CDDCH', "Chờ duyệt đặt chỗ"),
    ('DCH', "Đã đặt chỗ"),
    ('CDDCO', "Chờ duyệt đặt cọc"),
    ('DCO', 'Đã đặt cọc'),
    ('HDC', 'Hợp đồng giữ chỗ đặt cọc'),
    ('HUY', 'Huỷ')
]

class RealEstateOrder(models.Model):
    _name = 'real.estate.order'
    _description = 'Đơn hàng'

    order_code = fields.Char(string="Mã đơn hàng", readonly=True, store=True, default='New')
    property_name = fields.Char(string="Tài sản", required=True, help="Name of the real estate property", default="")
    transaction_status_id = fields.Many2one(
        comodel_name='real.estate.contract.status',
        string="Trạng thái giao dịch",
        required=True,
        default=lambda self: self.env['real.estate.contract.status'].search([('contract_status_code', '=', 'CDDCH')], limit=1).id,
        domain="[('contract_status_code', 'in', ['CDDCH', 'DCO', 'HDC'])]",
    )
    status = fields.Selection(SALE_ORDER_STATE, string="Trạng thái", default='CDDCH', required=True)
    property_status_id = fields.Many2one(
        comodel_name='real.estate.property.status',
        string="Trạng thái tài sản",
        required=True,
        default=lambda self: self.env['real.estate.property.status'].search([('status_code', '=', 'DCH')], limit=1).id,
        domain="[('status_code', 'in', ['DCH', 'DCO', 'HDC'])]",
    )
    booking_date = fields.Datetime(
        string="Ngày giữ chỗ",
        default=fields.Datetime.now,
    )
    deposit_date = fields.Datetime(
        string="Ngày đặt cọc",
    )
    description = fields.Char(string="Description", help="Description of the property")
    project_id = fields.Many2one(
        comodel_name='real.estate.project',
        string="Dự án",
        required=True,
    )
    building_id = fields.Many2one(
        comodel_name='real.estate.building',
        string="Toà nhà",
        domain="[('project_code', '=', project_id)]",
        require=True
    )
    property_id = fields.Many2one(
        comodel_name='real.estate.property',
        string="Tài sản",
        domain="[('building_id', '=', building_id)]",
        require=True
    )
    client_id = fields.Many2one(
        comodel_name='res.partner',
        string="Khách hàng",
        require=True
    )
    employee_id = fields.Many2one(
        comodel_name='hr.employee',
        string="Nhân viên phụ trách",
        default=lambda self: self._default_employee_id(),
    )
    booking_priority = fields.Integer(string="Số ưu tiên", readonly=True, store=True, default=0)
    payment_term_id = fields.Many2one(
        comodel_name='account.payment.term',
        string="Phương thức thanh toán",
        store=True
    )
    property_value = fields.Float(
        string="Giá trị tài sản",
        related='property_id.property_value',
        # readonly=True,
        store=True,
    )
    order_value = fields.Float(string="Giá trị đơn hàng", store=True)
    contract_count = fields.Integer(
        string="Số lượng Hợp đồng",
        compute="_compute_contract_count",
        store=True,
    )
    contract_ids = fields.One2many(
        comodel_name='real.estate.contract',  # The related model
        inverse_name='order_id',  # Field in the related model linking back to 'real.estate.order'
        string="Các hợp đồng"
    )
    cancel_date = fields.Datetime(  string="Ngày huỷ")
    invoice_count = fields.Integer(string="Số hoá đơn", compute='_get_invoiced')
    invoice_ids = fields.Many2many(
        comodel_name='account.move',
        string="Các hoá đơn",
        relation='real_estate_order_invoice_rel',  # Tên bảng liên kết
        column1='order_id',  # Trường tham chiếu tới booking
        column2='invoice_id',  # Trường tham chiếu tới account.move
        copy=False
    )
    def _get_invoiced(self):
        for order in self:
            # Truy vấn các hóa đơn đã liên kết với order hiện tại
            invoices = self.env['account.move'].search([
                ('booking_ids', '=', order.id)  # Thay 'booking_ids' bằng trường liên kết tương ứng
            ])
            # Gán các hóa đơn đã tìm được vào trường invoice_ids của order
            order.invoice_ids = [(6, 0, invoices.ids)]
            order.invoice_count = len(invoices)

    def action_view_contract(self, contracts=False):
        if not contracts:
            contracts = self.mapped('contract_ids')
        action = self.env['ir.actions.actions']._for_xml_id('transaction.real_estate_contract_action')
        if len(contracts) > 1:
            action['domain'] = [('id', 'in', contracts.ids)]
        elif len(contracts) == 1:
            form_view = [(self.env.ref('transaction.view_contract_form').id, 'form')]
            if 'views' in action:
                action['views'] = form_view + [(state,view) for state,view in action['views'] if view != 'form']
            else:
                action['views'] = form_view
            action['res_id'] = contracts.id
        else:
            action = {'type': 'ir.actions.act_window_close'}

        context = {
            'default_move_type': 'out_invoice',
        }
        if len(self) == 1:
            context.update({
                'default_partner_id': self.client_id.id,
                # 'default_partner_shipping_id': self.partner_shipping_id.id,
                'default_invoice_payment_term_id': self.payment_term_id.id or self.env['account.move'].default_get(['invoice_payment_term_id']).get('invoice_payment_term_id'),
                'default_invoice_origin': self.order_code,
            })
        action['context'] = context
        return action

    @api.depends()
    def _compute_contract_count(self):
        for order in self:
            order.contract_count = self.env['real.estate.contract'].search_count([
                ('order_id', '=', order.id)
            ])

    @api.onchange('project_id')
    def _onchange_project_id(self):
        self.building_id = False
        self.property_id = False
        return {'domain': {'building_id': [('project_code', '=', self.project_id.id)]}}

    @api.onchange('building_id')
    def _onchange_building_id(self):
        self.property_id = False
        return {'domain': {'property_id': [('building_id', '=', self.building_id.id)]}}

    @api.depends('order_code')
    def _compute_display_name(self):
        for order in self:
            order.display_name =  order.order_code
    @api.model
    def default_get(self, fields_list):
        """Set default values for fields"""
        defaults = super(RealEstateOrder, self).default_get(fields_list)
        return defaults
    def _default_employee_id(self):
        user = self.env.user
        employee = self.env['hr.employee'].search([('user_id', '=', user.id)])
        return employee.id if employee.id else False

    def create(self, vals):
        property = self.env['real.estate.property'].browse(vals.get('property_id'))
        if property.status_code != 'MBA' and 'status' in vals and vals.get('status') == 'DCH':
            raise ValidationError(f"Không thể tạo đặt cọc vì tòa nhà '{property.property_name}' chưa ở trạng thái 'Mở bán'.")
        last_order = self.env['real.estate.order'].search([], order='id desc', limit=1)
        if last_order and last_order.order_code:
            last_code_number = int(last_order.order_code[1:])
            next_code_number = last_code_number + 1
        else:
            next_code_number = 1
        vals['order_code'] = f"B{next_code_number:05d}"
        max_priority = self.env['real.estate.order'].search([('property_id', '=', property.id)], order='booking_priority desc', limit=1).booking_priority
        vals['booking_priority'] = max_priority + 1
        return super(RealEstateOrder, self).create(vals)

    def write(self, vals):
        if 'property_id' in vals:
            property = self.env['real.estate.property'].browse(vals['property_id'])
            if property.status_code != 'MBA' and vals.get('status') == 'DCH':
                raise ValidationError(
                    f"Không thể cập nhật đặt cọc vì tòa nhà '{property.property_name}' chưa ở trạng thái 'Mở bán'.")
        return super(RealEstateOrder, self).write(vals)

    def action_booking_confirm(self):
        dco_status = self.env['real.estate.contract.status'].search([('contract_status_code', '=', 'DCH')], limit=1)
        if not dco_status:
            raise ValueError("Trạng thái 'Đặt Cọc' chưa được thiết lập trong hệ thống.")

        self.transaction_status_id = dco_status.id
        self.status = 'DCH'
        return True

    def action_deposit_confirm(self):
        if self.property_id.status_code != 'MBA':
            raise ValidationError(
                f"Không thể cập nhật đặt cọc vì tòa nhà '{self.property_id.property_name}' chưa ở trạng thái 'Mở bán'.")
        dco_status = self.env['real.estate.contract.status'].search([('contract_status_code', '=', 'DCO')], limit=1)
        if not dco_status:
            raise ValueError("Trạng thái 'Đặt Cọc' chưa được thiết lập trong hệ thống.")

        self.transaction_status_id = dco_status.id
        self.status = 'DCO'
        return True
    def action_contract_confirm(self):
        hdc_status = self.env['real.estate.property.status'].search([('status_code', '=', 'HDC')], limit=1)
        if not hdc_status:
            raise ValueError("Trạng thái 'Hợp đồng cọc' chưa được thiết lập trong hệ thống.")

        self.property_status_id = hdc_status.id
        self.status = 'HDC'
        return True
    def action_deposit(self):
        cddco_status = self.env['real.estate.contract.status'].search([('contract_status_code', '=', 'CDDCO')], limit=1)
        if not cddco_status:
            raise ValueError("Trạng thái 'Đặt Cọc' chưa được thiết lập trong hệ thống.")

        self.transaction_status_id = cddco_status.id
        self.status = 'CDDCO'
        return True

    def action_cancel(self):
        huy_status = self.env['real.estate.contract.status'].search([('contract_status_code', '=', 'TLYHUY')], limit=1)
        if not huy_status:
            raise ValueError("Trạng thái 'Đặt Cọc' chưa được thiết lập trong hệ thống.")
        self.cancel_date = Datetime.now()
        self.transaction_status_id = huy_status.id
        self.status = 'HUY'
        return True

    def action_create_deposit_contract(self):
        for order in self:
            order.contract_count += 1;
            contract_vals = {
                'property_id': order.property_id.id,
                'contact_id': order.client_id.id,
                'contract_value': order.order_value,
                'order_id': order.id,
                'contract_status_code': order.transaction_status_id.contract_status_code,
                'property_code': order.property_id.property,
            }
            contract = self.env['real.estate.contract'].create(contract_vals)
            return {
                'type': 'ir.actions.act_window',
                'name': 'Contract',
                'view_mode': 'form',
                'res_model': 'real.estate.contract',
                'res_id': contract.id,
            }

    def action_create_booking_contract(self):
        for order in self:
            order.contract_count += 1
            contract_vals = {
                'property_id': order.property_id.id,
                'contact_id': order.client_id.id,
                'contract_value': order.order_value,
                'order_id': order.id,
                'contract_status_code': order.transaction_status_id.contract_status_code,
                'property_code': order.property_id.property,
                'deposit_value': order.order_value
            }
            contract = self.env['real.estate.contract'].create(contract_vals)
            return {
                'type': 'ir.actions.act_window',
                'name': 'Contract',
                'view_mode': 'form',
                'res_model': 'real.estate.contract',
                'res_id': contract.id,
            }

    def action_liquidation_deposit_contract(self):
        if self.property_id.status_code != 'HDC':
            raise ValidationError(
                f"Không thể cập nhật đặt cọc vì tòa nhà '{self.property_id.property_name}' chưa ở trạng thái 'Hợp đồng giữ chỗ'.")
        cdhdc_status = self.env['real.estate.contract.status'].search([('contract_status_code', '=', 'CDHDC')], limit=1)
        if not cdhdc_status:
            raise ValueError("Trạng thái 'Hợp đồng giữ chỗ' chưa được thiết lập trong hệ thống.")

        self.transaction_status_id = cdhdc_status.id
        self.status = 'HDC'
        for order in self:
            order.contract_count += 1
            contract_vals = {
                'property_id': order.property_id.id,
                'contact_id': order.client_id.id,
                'contract_value': order.order_value,
                'order_id': order.id,
                'contract_status_code': 'CDHDC',
                'property_code': order.property_id.property,
            }
            contract = self.env['real.estate.contract'].create(contract_vals)
            return {
                'type': 'ir.actions.act_window',
                'name': 'Contract',
                'view_mode': 'form',
                'res_model': 'real.estate.contract',
                'res_id': contract.id,
            }
        return True
