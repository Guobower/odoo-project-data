# -*- coding: utf-8 -*-

from odoo import models, fields, api


class AccountMoveLineInher(models.Model):
	_inherit = 'sale.order.line'


	crt_no           = fields.Char('Container Number')
	project_no       = fields.Char('Project Number')
	form             = fields.Many2one('from.qoute',string="From")
	to               = fields.Many2one('to.quote',string="To")
	fleet_type       = fields.Many2one('fleet',string="Fleet Type")
	product_id       = fields.Many2one('product.product',string='Product', required=False)
	

	@api.onchange('form','to','fleet_type')
	def add_charges(self):
		if self.order_id.partner_id.id and self.form.id and self.to.id and self.fleet_type:
			trans = self.env['res.partner'].search([('id','=',self.order_id.partner_id.id)])
			for x in trans.route_id:
				if self.form.id == x.form.id and self.to.id == x.to.id and self.fleet_type == x.fleet_type:
					self.price_unit = x.trans_charges
	
   
class transport_info(models.Model):
	_inherit = 'sale.order'
	# _rec_name   = 'company_name'

	suppl_name    = fields.Many2one('res.partner', string = "Supplier Name",required=True)
	suppl_freight = fields.Char(string='Supplier Freight')
	bill_type     = fields.Char(string='Billing Type')
	bill_no       = fields.Char(string='B/L Number')
	freight_link  = fields.Many2one('freight.forward',string='Freight Forwarding',readonly=True)
	trans_link    = fields.Many2one('freight.forward',string='Freight Link',readonly=True)
	acc_link      = fields.Many2one('account.invoice',string='Invoice',readonly=True)
	inter_num     = fields.Integer(string="Internal Number")
	driver        = fields.Char(string = "Driver")
	driver_num    = fields.Char(string = "Driver Number")
	form_t        = fields.Many2one('from.qoute',string="From")
	to_t          = fields.Many2one('to.quote',string="To")
	fleet_type    = fields.Many2one('fleet',string="Fleet Type")
	upload_date   = fields.Date(string="Loading Date")
	delivery_date = fields.Date(string="Arrival Date")
	return_date   = fields.Date(string="Return Date")
	stuff_date    = fields.Date(string="Stuffing Date")
	recive_name   = fields.Char(string="Receiver Name")
	recive_mob    = fields.Char(string="Receiver Mobile")
	sales_id      = fields.Many2one('export.logic')
	state         = fields.Selection([
					('draft', 'Quotation'),
					('sent', 'Quotation Sent'),
					('sale', 'Sales Order'),
					('done', 'Locked'),
					('cancel', 'Cancelled'),
					('rec', 'Received POD'),
					], string='Status', readonly=True, copy=False, index=True, track_visibility='onchange', default='draft')


	@api.onchange('partner_id')
	def get_bill(self):
		records = self.env['res.partner'].search([('id','=',self.partner_id.id)])
		if self.partner_id:
			self.bill_type = records.bill_type

	@api.multi
	def receive(self):
		self.state = "rec"
		purchase_order = self.env['sale.order'].search([('name','=',self.name)])
		invoice = self.env['account.invoice'].search([])
		invoice_lines = self.env['account.invoice.line'].search([])

		if purchase_order:
			create_invoice = invoice.create({
				'journal_id': 1,
				'partner_id':self.suppl_name.id,
				'date_invoice' : purchase_order.date_order,
				'type':"in_invoice",
				})
			for x in purchase_order.order_line:
				create_invoice_lines= invoice_lines.create({
					'product_id':1,
					'quantity':x.product_uom_qty,
					'price_unit':purchase_order.suppl_freight,
					'crt_no':x.crt_no,
					'account_id': 3,
					'name' : x.name,
					'invoice_id' : create_invoice.id
					})

	@api.multi
	def somethinghappens(self):
		self.action_confirm()
		self.action_invoice_create()
		self.state = "rec"


	@api.onchange('form','to','fleet_type')
	def add_charges(self):
		if self.suppl_name and self.form_t.id and self.to_t.id and self.fleet_type:
			trans = self.env['res.partner'].search([('id','=',self.suppl_name.id)])
			for x in trans.route_id:
				if self.form_t.id == x.form.id and self.to_t.id == x.to.id and self.fleet_type == x.fleet_type:
					self.suppl_freight = x.trans_charges


class AccountInvoiceTree(models.Model):
	_inherit = 'account.invoice.line'

	crt_no       = fields.Char('Container No.')



class AccountInvoiceForm(models.Model):
	_inherit = 'account.invoice'
	acount_link = fields.Many2one('freight.forward',string='link')







