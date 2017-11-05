# -*- coding: utf-8 -*- 
from odoo import models, fields, api
from openerp.osv import osv
from openerp.exceptions import Warning
from openerp.exceptions import ValidationError
import datetime
from datetime import datetime,date,timedelta,time
import dateutil.parser
from dateutil.relativedelta import relativedelta
from itertools import groupby
import collections
from collections import namedtuple
import json
import time
from odoo import api, fields, models, _
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.tools.float_utils import float_compare
from odoo.addons.procurement.models import procurement
from odoo.exceptions import UserError



class sale_invoice_customized(models.Model):
	_inherit = 'account.invoice'

	due_days = fields.Integer(string="Due Days",compute="compute_remaining_days")
	due = fields.Char(string="Due")
	transporter = fields.Many2one('res.partner',string="Transporter")
	incoterm = fields.Many2one('stock.incoterms')
	check_direct_invoice = fields.Boolean('Direct Invoice', default=True)
	remaining_payment_days =fields.Date('Remaining Payment Days')
	reference = fields.Char(string="Reference")
	pay_tree_id = fields.One2many('invoice.payment','pay_tree')
	balance = fields.Float(string="Balance")
	source = fields.Char(string="Source")
	del_records = fields.Many2one('sale.order')
	warehouse = fields.Many2one('stock.warehouse',string="Warehouse")
	stock_id = fields.Many2one('stock.picking',string="Stock Link")
	waveoff_amount 	= fields.Float(string="Discount")
	pdc_module = fields.Many2one('pdc_bcube.pdc_bcube', string="Checks And Balance")
	state = fields.Selection([
	('draft', 'Draft'),
	('refund', 'Refund'),
	('proforma', 'Pro-forma'),
	('proforma2', 'Pro-forma'),
	('open', 'Open'),
	('paid', 'Paid'),
	('cancel', 'Cancelled'),
	], string='Status', readonly=True, copy=False, index=True, track_visibility='onchange', default='draft')




	@api.multi
	def action_invoice_open(self):
		if self.state != 'open':
			if self.payment_term_id.name == 'Immediate Payment':
				JournalEntries = self.env['account.move'].search([('partner_id','=',self.partner_id.id)])
				amount = 0
				for rec in JournalEntries:
					for line in rec.line_ids:
						if line.account_id.id == self.partner_id.property_account_receivable_id.id:
							amount += line.debit - line.credit
				amount += self.amount_total
				if amount > 0:
					return {
					'type': 'ir.actions.act_window',
					'name': 'Customer Receipts',
					'res_model': 'customer.payment.bcube',
					'view_type': 'form',
					'view_mode': 'form',
					'target' : 'new',
					'context': {'default_partner_id': self.partner_id.id,'default_receipts': True}
					}		
		if not self.pdc_module:
			if self.payment_term_id.name == 'Cheque Before Delivery':
				self.state == 'draft'
				return {
				'type': 'ir.actions.act_window',
				'name': 'Cheque And Balance',
				'res_model': 'pdc_bcube.pdc_bcube',
				'view_type': 'form',
				'view_mode': 'form',
				'target' : 'new',
				'context': {'default_customer': self.partner_id.id, 'default_inv_ref': self.id}
				}
		credit1 = self.partner_id.credit + self.amount_total
		credit_limit1 = self.partner_id.credit_limit
		stop = self.partner_id.stop_invoice
		self._check_total(credit1,credit_limit1,stop)
		res = super(sale_invoice_customized, self).action_invoice_open()
		rec = self.env['stock.picking'].search([('id','=',self.stock_id.id)])
		if self.stock_id.id:
			rec.print_do = True
		sale_order = self.env['sale.order'].search([('name','=',self.source)])
		count = 0
		if self.source:
			if sale_order.direct_invoice_check == False:
				for x in sale_order.picking_ids:
					if x.state == 'done':
						count = count + 1
				if count == len(sale_order.picking_ids):
					sale_order.state = 'complete'
		return res


	@api.multi
	@api.constrains()
	def _check_total(self,credit,credit_limit,stop):
		if stop == True:
			if credit > credit_limit:
				raise ValidationError('Amount is exceeding credit limit')

	@api.one
	def compute_remaining_days(self):
		current_date = fields.date.today()
		current_date = str(current_date)
		if self.date_invoice and self.payment_term_id and self.remaining_payment_days:
			fmt = '%Y-%m-%d'
			d1 = datetime.strptime(current_date, fmt)
			d2 = datetime.strptime(self.remaining_payment_days, fmt)
			self.due_days = str((d1-d2).days)


	@api.multi
	def to_refund(self):
		self.state = 'refund'

		stock_pick = self.env['stock.picking.type'].search([('warehouse_id.id','=',self.warehouse.id)])
		new = 0
		for x in stock_pick:
			if x.name == 'Receipts':
				new = x.id


		inventory = self.env['stock.picking']
		inventory_lines = self.env['stock.pack.operation'].search([])
		inventory_lines_move = self.env['stock.move'].search([])
		create_inventory = inventory.create({
			'partner_id':self.partner_id.id,
			'location_id':15,
			'refund': True,
			'picking_type_id' : new,
			'location_dest_id' : 9,
			'account_inv_id':self.id,

		})

		for x in self.invoice_line_ids:
			create_inventory_lines= inventory_lines.create({
				'product_id':x.product_id.id,
				'carton_to':x.quantity,
				'qty_done': x.quantity,
				'location_id':15,
				'location_dest_id': 9,
				'picking_id': create_inventory.id,
				})
		# for x in self.invoice_line_ids:
		# 	create_inventory_lines_move= inventory_lines_move.create({
		# 				'product_id':x.product_id.id,
		# 				'product_uom_qty':x.quantity,
		# 				'product_uom': x.product_id.uom_id.id,
		# 				'location_id':15,
		# 				'picking_id': create_inventory.id,
		# 				'name':"test",
		# 				'location_dest_id': 9,
		# 				})


	# @api.model
	# def create(self, vals):
		
	#   new_record = super(sale_invoice_customized, self).create(vals)
	#   credit1 = new_record.partner_id.credit + new_record.amount_total
	#   credit_limit1 = new_record.partner_id.credit_limit
	#   stop = new_record.partner_id.stop_invoice
	#   self._check_total(credit1,credit_limit1,stop)

	#   return new_record

	# @api.multi
	# def write(self, vals):
	# 	super(sale_invoice_customized, self).write(vals)
	# 	credit1 = self.partner_id.credit + self.amount_total
	# 	credit_limit1 = self.partner_id.credit_limit
	# 	stop = self.partner_id.stop_invoice
	# 	self._check_total(credit1,credit_limit1,stop)
	# 	return True


class sale_invoice_line_extension(models.Model):
	_inherit = "account.invoice.line"

	uom = fields.Char(string="UOM", readonly="1")
	carton = fields.Float(string="Quantity (CARTONS)")
	cartons = fields.Float(string="Cartons")
	last_sale = fields.Float(string="Last Sale")  
	promo_code 		= fields.Many2one('naseem.sales.promo',string="PROMO CODE",readonly=True)
	customer_price = fields.Float(string="Net Price")
	price = fields.Many2one('product.pricelist.item')


	@api.onchange('product_id')
	def _onchange_unit_price(self):
		if self.invoice_id.type == "out_refund":
			l_date = []
			rec = self.env['account.invoice'].search([('partner_id.id','=',self.invoice_id.partner_id.id)])
			for x in rec:
				for y in x.invoice_line_ids:
					if self.product_id.id == y.product_id.id:
						l_date.append(x)
						datelist = sorted(l_date, key=lambda x: x.date_invoice)
						new = datelist.pop().date_invoice
			for data in rec:
				for y in data.invoice_line_ids:
					if self.product_id.id == y.product_id.id:
						if data.date_invoice == new:
							self.price_unit = y.price_unit
							print y.price_unit

	@api.onchange('quantity')
	def _onchange_cartons(self):
		if self.invoice_id.type == "out_refund":
			if self.quantity > 1:
				self.cartons = self.quantity / self.product_id.pcs_per_carton





