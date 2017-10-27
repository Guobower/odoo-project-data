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


class stock_picking_own(models.Model):
	_inherit 	= 'stock.picking'
	backorder 		= fields.Boolean(string="Back Order", invisible=True)
	bilty_no  		= fields.Char(string="Billty No.")
	del_records     = fields.Many2one('sale.order')
	cash_book_id    = fields.Many2one('account.bank.statement',string="Cash Book")
	print_do 		= fields.Boolean(string="Print DC")
	direct_inv		= fields.Boolean(string="Direct Invoice")
	inv_type		= fields.Char(string="Invoice Type")
	# bilty_recieved  = fields.Float(string="Billty Expense Received")
	packing_expense = fields.Float(string="Packing Expense")
	bilty_paid 		= fields.Float(string="Billty Amount")
	received_by 	= fields.Char(string="Received by")
	transporter 	= fields.Many2one('res.partner',string="Transporter")

	reference_no 	= fields.Char(string="Reference No.")
	carton_no		= fields.Char(string="No. of Carton")
	bundle_no		= fields.Char(string="No. of Bundles")
	delivered_by	= fields.Char(string="Delivered By")
	warehouse 		= fields.Many2one('account.bank.statement',string="Cash Account")

	state = fields.Selection([
		('draft', 'Draft'),
		('cancel', 'Cancelled'),
		('waiting', 'Waiting Another Operation'),
		('confirmed', 'Waiting Availability'),
		('partially_available', 'Partially Available'),
		('assigned', 'Available'),
		('done', 'Done'),
		('close', 'Closed'),
		], string='Status', readonly=True, copy=False, index=True, track_visibility='onchange', default='draft')



	@api.multi
	def submitt_bilty(self):

		if self.cash_book_id:
			for x in self.cash_book_id:
				for y in x.line_ids:
					if y.bilty_link.id == self.id:
						y.date = self.min_date
						y.name = self.reference_no
						y.ref= self.reference_no
						y.partner = self.partner_id.id
						y.amount = self.bilty_paid + self.packing_expense
		else:
			cash_enteries = self.env['account.bank.statement'].search([('journal_id.name','=',self.warehouse.name),('state','=','open')])
			if cash_enteries:
					inv = []
					inv.append({
						'date':self.min_date,
						'name':self.reference_no,
						'partner_id':self.partner_id.id,
						'ref':self.reference_no,
						'amount':self.bilty_paid + self.packing_expense,
						'bilty_link': self.id,
						'line_ids':cash_enteries.id,
						})

					self.cash_book_id = cash_enteries.id
					
					cash_enteries.line_ids = inv
					inv=[]
			else:
				raise ValidationError('Open Concerned Cash Book First')



	def do_new_transfer(self):
		new_record = super(stock_picking_own, self).do_new_transfer()
		if self.direct_inv == True and self.inv_type == 'credit':
			sale_order = self.env['sale.order'].search([('name','=',self.origin)])
			purchase_order = self.env['purchase.order'].search([('name','=',self.origin)])
			
			# invoice = self.env['account.invoice'].search([])
			# invoice_lines = self.env['account.invoice.line'].search([])
			self._invoice_creation_sale(sale_order ,self.pack_operation_product_ids)

			# if purchase_order:
			# 	create_invoice = invoice.create({
			# 		'journal_id': 3,
			# 		'partner_id':purchase_order.partner_id.id,
			# 		'transporter':purchase_order.transporter.id,
			# 		# 'remaining_payment_days':purchase_order.remaining_payment_days,
			# 		# 'due' : purchase_order.due,
			# 		# 'user_id' : purchase_order.user_id.id,
			# 		'payment_term_id' : purchase_order.payment_term_method.id,
			# 		# 'due_days' : purchase_order.due_days,
			# 		'date_invoice' : purchase_order.date_order,
			# 		'incoterm' : purchase_order.incoterm.id,
			# 		'type':"in_invoice",
			# 		})

			# 	for x in purchase_order.order_line:
			# 		amt = 0
			# 		for y in self.pack_operation_product_ids:
			# 			amt = amt + y.qty_done
			# 		qty = 0
			# 		if amt == 0:
			# 			qty = y.product_qty
			# 		else:
			# 			qty = y.qty_done
			# 		for y in self.pack_operation_product_ids:
			# 			if x.product_id.id == y.product_id.id:
			# 				if x.product_id.property_account_income_id.id:
			# 					account_id = x.product_id.property_account_income_id.id
			# 				else:
			# 					account_id = x.product_id.categ_id.property_account_income_categ_id	
			# 				create_invoice_lines= invoice_lines.create({
			# 					'product_id':x.product_id.id,
			# 					# 'uom':x.uom,
			# 					'quantity': qty,
			# 					'carton': qty/x.product_id.pcs_per_carton,
			# 					# 'last_sale': x.last_sale,
			# 					# 'price': x.price.id,
			# 					'price_unit': x.price_unit,
			# 					# 'discount': x.discount,
			# 					# 'customer_price': x.customer_price,
			# 					'price_subtotal': x.price_subtotal,
			# 					# 'promo_code': x.promo_code,
			# 					'account_id': 3,
			# 					'name' : x.name,
			# 					'invoice_id' : create_invoice.id
			# 					})

		return new_record

	def action_assign(self):
		new_record = super(stock_picking_own, self).action_assign()
		for y in self.pack_operation_product_ids:
			y.carton_to = y.product_qty / y.product_id.pcs_per_carton
			print y.carton_to
			print "kkkkkkkkkkkkkkkkkkkkkk"
			print "kkkkkkkkkkkkkkkkkkkkkk"

		return new_record


	def _invoice_creation_sale(self, sale_order ,pack_operation_product_ids):
		# sale_order = self.env['sale.order'].search([('name','=',self.origin)])
		# purchase_order = self.env['purchase.order'].search([('name','=',self.origin)])
			
		invoice = self.env['account.invoice'].search([])
		invoice_lines = self.env['account.invoice.line'].search([])
		if sale_order:
			create_invoice = invoice.create({
				'journal_id': sale_order.journal.id,
				'partner_id':sale_order.partner_id.id,
				'transporter':sale_order.transporter.id,
				'remaining_payment_days':sale_order.remaining_payment_days,
				'due' : sale_order.due,
				'user_id' : sale_order.user_id.id,
				'payment_term_id' : sale_order.payment_term_id.id,
				'due_days' : sale_order.due_days,
				'date_invoice' : sale_order.date_order,
				'incoterm' : sale_order.incoterm.id,
				'source' : sale_order.name,
				})

			for x in sale_order.order_line:
				amt = 0
				qty = 0
				for y in pack_operation_product_ids:
					amt = amt + y.qty_done
				
				# 	if amt == 0:
				# 		qty = y.product_qty
				# else:
				# 	qty = y.qty_done
				for y in pack_operation_product_ids:
					if amt == 0:
						qty = y.product_qty
					else:
						qty = y.qty_done
					if x.product_id.id == y.product_id.id:
						if x.product_id.property_account_income_id.id:
							account_id = x.product_id.property_account_income_id.id
						else:
							account_id = x.product_id.categ_id.property_account_income_categ_id.id	
						create_invoice_lines= invoice_lines.create({
							'product_id':x.product_id.id,
							'uom':x.uom,
							'quantity': qty,
							'carton': qty/x.product_id.pcs_per_carton,
							'last_sale': x.last_sale,
							'price': x.price.id,
							'price_unit': x.price_unit,
							'discount': x.discount,
							'customer_price': x.customer_price,
							'price_subtotal': x.price_subtotal,
							'promo_code': x.promo_code.id,
							'account_id': account_id,
							'name' : x.name,
							'invoice_id' : create_invoice.id,
							})

	@api.multi
	def _create_backorder(self, backorder_moves=[]):
		""" Move all non-done lines into a new backorder picking. If the key 'do_only_split' is given in the context, then move all lines not in context.get('split', []) instead of all non-done lines.
		"""
		# TDE note: o2o conversion, todo multi

		backorders = self.env['stock.picking']
		for picking in self:
			backorder_moves = backorder_moves or picking.move_lines
			if self._context.get('do_only_split'):
				not_done_bo_moves = backorder_moves.filtered(lambda move: move.id not in self._context.get('split', []))
			else:
				not_done_bo_moves = backorder_moves.filtered(lambda move: move.state not in ('done', 'cancel'))
			if not not_done_bo_moves:
				continue
			backorder_picking = picking.copy({
				'name': '/',
				'move_lines': [],
				'pack_operation_ids': [],
				'backorder_id': picking.id,
				'backorder':True,
			})
			picking.message_post(body=_("Back order <em>%s</em> <b>created</b>.") % (backorder_picking.name))
			not_done_bo_moves.write({'picking_id': backorder_picking.id})
			if not picking.date_done:
				picking.write({'date_done': time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)})
			backorder_picking.action_confirm()
			backorder_picking.action_assign()
			backorders |= backorder_picking



		purchase_order = self.env['purchase.order'].search([('name','=',self.origin)])
		sale_order = self.env['sale.order'].search([('name','=',self.origin)])
		if purchase_order:
			purchase_order.state = "partial"
		if sale_order:
			sale_order.state= "partial"

		return backorders




class stock_pack_extension(models.Model):
	_inherit 	= 'stock.pack.operation'

	carton_to 	= fields.Float(string="Carton To Do")
	carton_done = fields.Float(string="Carton Done")

	@api.onchange('product_qty')
	def calculate_cartons_to(self):
		if self.product_qty:
			self.carton_to = int(self.product_qty / self.product_id.pcs_per_carton)

	@api.onchange('carton_to')
	def round_carton_to(self):
		if self.carton_to:
			self.carton_to = round(self.carton_to)

			# self.qty_done = self.product_id.pcs_per_carton * self.product_qty
			# self.carton_done = self.qty_done / self.product_id.pcs_per_carton 

	@api.onchange('carton_done')
	def calculate_cartons_done(self):
		if self.carton_done:
			self.carton_done = round(self.carton_done)
			self.qty_done = int(self.product_id.pcs_per_carton * self.carton_done)


	@api.onchange('qty_done')
	def calculate_qty_done(self):
		if self.qty_done:
			self.qty_done = round(self.qty_done)
			self.carton_done =  int(self.qty_done / self.product_id.pcs_per_carton)

class stock_immediate_transfer_naseem(models.TransientModel):
	_inherit 	= 'stock.immediate.transfer'

	def process(self):
		result = super(stock_immediate_transfer_naseem, self).process()
		stock_picking_id = self.env['stock.picking'].search([('name','=',self.pick_id.name)])
		sale_order = self.env['sale.order'].search([('name','=',stock_picking_id.origin)])
		stock_picking_id._invoice_creation_sale(sale_order, stock_picking_id.pack_operation_product_ids)
		return result

class stock_backorder_transfer_naseem(models.TransientModel):
	_inherit 	= 'stock.backorder.confirmation'

	def process(self):
		result = super(stock_backorder_transfer_naseem, self).process()
		stock_picking_id1 = self.env['stock.picking'].search([('name','=',self.pick_id.name)])
		sale_order = self.env['sale.order'].search([('name','=',stock_picking_id1.origin)])
		stock_picking_id1._invoice_creation_sale(sale_order, stock_picking_id1.pack_operation_product_ids)
		return result
