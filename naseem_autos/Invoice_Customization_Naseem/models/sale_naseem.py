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

class sale_order_customized(models.Model):
	_inherit = 'sale.order'

	due_days 				= fields.Integer(string="Due Days", compute="compute_remaining_days")
	due 					= fields.Char(string="Due")
	transporter 			= fields.Many2one('res.partner',string="Transporter")
	delivery_id 			= fields.Many2one('stock.picking',string="Delivery Id",readonly=True)
	remaining_payment_days  = fields.Datetime(string="Remaining Payment Days")
	direct_invoice_check 	= fields.Boolean(string="Direct Invoice", readonly="1")
	saleperson_check 	    = fields.Boolean(string="check", readonly="1")
	journal 				= fields.Many2one('account.journal', string="Journal")
	types = fields.Selection([('cash', 'Cash'),('credit', 'Credit')],string="Type")
	state2 = fields.Selection([
	('draft', 'Draft'),
	('validate', 'Validate'),
	('cancel', 'Cancelled'),
	], string='Status', readonly=True, copy=False, index=True, track_visibility='onchange', default='draft')
	
	state = fields.Selection([
	('draft', 'Quotation'),
	('sent', 'Quotation Sent'),
	('sale', 'Sales Order'),
	('done', 'Locked'),
	('assigned', 'Collect Cargo'),
	('waiting_approve', 'Waiting For Approval'),
	('ready', 'Ready For Delivery'),
	('cancel', 'Cancelled'),
	('partial', 'Partial'),
	('complete', 'Complete'),
	], string='Status', readonly=True, copy=False, index=True, track_visibility='onchange', default='draft')

	@api.multi
	def make_delivery(self):
		sale_deliveries = self.env['stock.picking'].search([('origin','=',self.name),('backorder','=',True)])
		if sale_deliveries:
			sale_deliveries.backorder = False
		else:
			raise ValidationError('No Pending Delivery Exists for this Sale Order')

	@api.multi
	def complete_order(self):
		return {
		'type': 'ir.actions.act_window',
		'name': 'Add Products',
		'res_model': 'sale.approve',
		'view_type': 'form',
		'view_mode': 'form',
		'target' : 'new',
		}
		# if self.direct_invoice_check == True:
		# 	self.state2 = "complete"
		# else:
		# 	self.state = "complete"
		# back_order = self.env['stock.picking'].search([('origin','=',self.name),('state','not in',('done','cancel'))])
		# if back_order:
		# 	print "Found"
		# 	print "xxxxXXXxxxXXXXxxxxxxxxxxx"
		# 	back_order.state = "cancel"


	@api.multi
	def generate_wizard(self):
		return {
		'type': 'ir.actions.act_window',
		'name': 'Add Products',
		'res_model': 'wizard.class',
		'view_type': 'form',
		'view_mode': 'form',
		'target' : 'new',
		}

	# incoterm = fields.Many2one('stock.incoterms')
	due = fields.Char()
###################################################
	instant_promo = fields.One2many('instant.promo.so','instant_promo_id')

	@api.onchange('instant_promo')
	def get_per_carton(self):

		for x in self.instant_promo:
			if x.qty > 0:
				if x.product_id.pcs_per_carton > 0:
					x.qty_per_crt = x.qty / x.product_id.pcs_per_carton

	@api.one
	def compute_remaining_days(self):
		current_date = fields.Datetime.now()
		if self.date_order and self.payment_term_id and self.remaining_payment_days:
			fmt = '%Y-%m-%d %H:%M:%S'
			d1 = datetime.strptime(current_date, fmt)
			d2 = datetime.strptime(self.remaining_payment_days, fmt)
			self.due_days = str((d1-d2).days)

	@api.onchange('partner_id')
	def select_journal(self):
		journal_env_cash = self.env['account.journal'].search([('type','=',"cash")])
		journal_env_sale = self.env['account.journal'].search([('type','=',"sale")])

		if self.partner_id:	
			self.transporter = self.partner_id.transporter
			self.payment_term_id = self.partner_id.payment_term
			self.incoterm = self.partner_id.incoterm
			self.currency_id = self.partner_id.currency
			if self.partner_id.user_id:
				self.user_id = self.partner_id.user_id.id
				self.saleperson_check = True
			else:
				users = self.env['res.users'].search([('id','=',self._uid)])
				self.user_id = users.id
				self.saleperson_check = False
			if self.direct_invoice_check == False:
				sale_journal = self.env['account.journal'].search([('type','=','sale')])
				self.journal = sale_journal.id



	@api.onchange('types')
	def _cash_types(self):
		if self.types:
			if self.types == 'cash':
				check = self.env['hr.employee'].search([('user_id.id','=',self.user_id.id)])
				if check.cash_book:
					self.journal = check.cash_book.id
			else:
				sale_journal = self.env['account.journal'].search([('type','=','sale')])
				self.journal = sale_journal.id


	@api.onchange('payment_term_id','date_order')
	def count_total(self):
		if self.date_order and self.payment_term_id:
			date_start_dt = fields.Datetime.from_string(self.date_order)
			dt 	= date_start_dt + relativedelta(days=self.payment_term_id.line_ids.days)
			self.remaining_payment_days = fields.Datetime.to_string(dt)
			fmt = '%Y-%m-%d %H:%M:%S'
			d1 = datetime.strptime(self.date_order, fmt)
			d2 = datetime.strptime(self.remaining_payment_days, fmt)
			self.due_days = str((d1-d2).days)

	@api.multi
	def validate_direct_invoice(self):
		self.state2 = 'validate'

#####################################
#  Create Customer Invoice  
#####################################

		sale_order = self.env['sale.order'].search([('partner_id','=',self.partner_id.id),(('state','=',"sale"))])
		total = 0 
		for x in sale_order:
			total = total + x.amount_total

		if self.types == 'cash':
			cash_enteries = self.env['account.bank.statement'].search([('journal_id.name','=',self.journal.name),('state','=','open')])
			if cash_enteries:
				inv = []
				for invo in self.order_line:
					inv.append({
						'date':self.date_order,
						'name':"payment",
						'partner_id':self.partner_id.id,
						'ref':self.name,
						'amount':self.amount_total,
						'line_ids':cash_enteries.id,
						})
				
				cash_enteries.line_ids = inv
				inv=[]
			else:
				raise ValidationError('Open Concerned Cash Book First')


			inventory = self.env['stock.picking']
			inventory_lines = self.env['stock.move'].search([])
			create_inventory = inventory.create({
				'partner_id':self.partner_id.id,
				'del_records':self.id,
				'location_id':15,
				'direct_inv': True,
				'inv_type': self.types,
				'print_do': True,
				'transporter': self.transporter.id,
				'picking_type_id' : 4,
				'location_dest_id' : 9,
				'origin':self.name,

			})

			self.delivery_id = create_inventory.id

			for x in self.order_line:
				create_inventory_lines= inventory_lines.create({
					'product_id':x.product_id.id,
					'product_uom_qty':x.product_uom_qty,
					'product_uom': x.product_id.uom_id.id,
					'location_id':15,
					'picking_id': create_inventory.id,
					'name':"test",
					'location_dest_id': 9,
					})
			create_inventory.action_assign()
			for x in create_inventory:
				for y in x.pack_operation_product_ids:
					y.carton_to = y.product_qty / y.product_id.pcs_per_carton
					y.qty_done = y.product_qty
					y.carton_done = y.carton_to
			create_inventory.do_new_transfer()

		if self.types == 'credit':

			# invoice = self.env['account.invoice'].search([])
			# invoice_lines = self.env['account.invoice.line'].search([])
			# create_invoice = invoice.create({
			# 	'journal_id': self.journal.id,
			# 	'partner_id':self.partner_id.id,
			# 	'transporter':self.transporter.id,
			# 	'remaining_payment_days':self.remaining_payment_days,
			# 	'due' : self.due,
			# 	'user_id' : self.user_id.id,
			# 	'payment_term_id' : self.payment_term_id.id,
			# 	'due_days' : self.due_days,
			# 	'date_invoice' : self.date_order,
			# 	'incoterm' : self.incoterm.id,
			# 	'del_records' : self.id,
			# 	'balance' : total,
			# 	'state2' : "confirm"
			# 	})

			# for x in self.order_line:
			# 	if x.product_id.property_account_income_id.id:
			# 		account_id = x.product_id.property_account_income_id.id
			# 	else:
			# 		account_id = x.product_id.categ_id.property_account_income_categ_id.id	
			# 	create_invoice_lines= invoice_lines.create({
			# 		'product_id':x.product_id.id,
			# 		'uom':x.uom,
			# 		'quantity': x.product_uom_qty,
			# 		'carton': x.carton,
			# 		'last_sale': x.last_sale,
			# 		'price': x.price.id,
			# 		'price_unit': x.price_unit,
			# 		'discount': x.discount,
			# 		'customer_price': x.customer_price,
			# 		'price_subtotal': x.price_subtotal,
			# 		'promo_code': x.promo_code.id,
			# 		'account_id':account_id,
			# 		'name' : x.name,
			# 		'invoice_id' : create_invoice.id
			# 		})	

			inventory = self.env['stock.picking']
			inventory_lines = self.env['stock.move'].search([])
			create_inventory = inventory.create({
				'partner_id':self.partner_id.id,
				'del_records':self.id,
				'location_id':15,
				'direct_inv': True,
				'inv_type': self.types,
				'transporter': self.transporter.id,
				'print_do': True,
				'picking_type_id' : 4,
				'location_dest_id' : 9,
				'origin':self.name,

			})

			self.delivery_id = create_inventory.id

			for x in self.order_line:
				create_inventory_lines= inventory_lines.create({
					'product_id':x.product_id.id,
					'product_uom_qty':x.product_uom_qty,
					'product_uom': x.product_id.uom_id.id,
					'location_id':15,
					'picking_id': create_inventory.id,
					'name':"test",
					'location_dest_id': 9,
					})
				
			create_inventory.action_assign()
			for x in create_inventory:
				for y in x.pack_operation_product_ids:
					y.carton_to = y.product_qty / y.product_id.pcs_per_carton
					y.qty_done = y.product_qty
					y.carton_done = y.carton_to
			create_inventory.state = 'done'
			create_inventory.do_new_transfer()

	#####################################
	#  Create Stock Entry 
	#####################################

		# inventory = self.env['stock.picking']
		# inventory_lines = self.env['stock.move'].search([])
		# create_inventory = inventory.create({
		# 	'partner_id':self.partner_id.id,
		# 	'cancel':self.id,
		# 	'location_id':15,
		# 	'picking_type_id' : 4,
		# 	'location_dest_id' : 9,

		# 	})
		# for x in self.order_line:
		# 	create_inventory_lines= inventory_lines.create({
		# 		'product_id':x.product_id.id,
		# 		'product_uom_qty':x.product_uom_qty,
		# 		'product_uom': x.product_id.uom_id.id,
		# 		'location_id':15,
		# 		'picking_id': create_inventory.id,
		# 		'name':"test",
		# 		'location_dest_id': 9,
		# 		})

	#####################################
	#  Create Journal Entry 
	#####################################
		# journal_entries = self.env['account.move'].search([('promo_id','=',self.id)])
		# journal_entries_lines = self.env['account.move.line'].search([])
		# if not journal_entries:
		# 	create_journal_entry = journal_entries.create({
		# 		'journal_id': self.journal.id,
		# 		'date':self.date_order,
		# 		'promo_id':self.id,
		# 		# 'ref':active_class.order_no,
		# 		})
			
		# 	create_debit = journal_entries_lines.create({
		# 		'account_id':1,
		# 		'partner_id':self.partner_id.id,
		# 		'name':"test",
		# 		'debit':self.amount_total,
		# 		'move_id':create_journal_entry.id
		# 		})
		# 	create_credit = journal_entries_lines.create({
		# 		'account_id':3,
		# 		'partner_id':self.partner_id.id,
		# 		'name':"test",
		# 		'credit':self.amount_total,
		# 		'move_id':create_journal_entry.id
		# 		})

		# else:
		# 	for x in journal_entries:
		# 		for y in x.line_ids:
		# 			if y.debit ==0:
		# 				y.credit=self.amount_total

		# 			if y.credit ==0:
		# 				y.debit=self.amount_total

	# @api.multi
	# def validate_sale_order(self):
	# 	invoice = self.env['account.invoice'].search([])
	# 	invoice_lines = self.env['account.invoice.line'].search([])
	# 	create_invoice = invoice.create({
	# 		'journal_id': self.journal.id,
	# 		'partner_id':self.partner_id.id,
	# 		'transporter':self.transporter.id,
	# 		'remaining_payment_days':self.remaining_payment_days,
	# 		'due' : self.due,
	# 		'user_id' : self.user_id.id,
	# 		'payment_term_id' : self.payment_term_id.id,
	# 		'due_days' : self.due_days,
	# 		'date_invoice' : self.date_order,
	# 		'incoterm' : self.incoterm.id,
	# 		})

	# 	for x in self.order_line:
	# 		if x.product_id.property_account_income_id.id:
	# 			account_id = x.product_id.property_account_income_id.id
	# 		else:
	# 			account_id = x.product_id.categ_id.property_account_income_categ_id	
	# 		create_invoice_lines= invoice_lines.create({
	# 			'product_id':x.product_id.id,
	# 			'uom':x.uom,
	# 			'quantity': x.product_uom_qty,
	# 			'carton': x.carton,
	# 			'last_sale': x.last_sale,
	# 			'price': x.price.id,
	# 			'price_unit': x.price_unit,
	# 			'discount': x.discount,
	# 			'customer_price': x.customer_price,
	# 			'price_subtotal': x.price_subtotal,
	# 			'promo_code': x.promo_code,
	# 			'account_id': account_id.id,
	# 			'name' : x.name,
	# 			'invoice_id' : create_invoice.id
	# 			})	

	@api.multi
	def cancel_invoice(self):
		self.state2 = 'cancel'

		del_stock = self.env['stock.picking'].search([('del_records','=',self.id)])
		del_stock.unlink()
		del_invoice = self.env['account.invoice'].search([('del_records','=',self.id)])
		del_invoice.unlink()
		del_journal = self.env['account.bank.statement'].search([('journal_id.name','=',self.journal.name),('state','=','open')])
		if del_journal:
			for x in del_journal.line_ids:
				if x.ref == self.name:
					x.unlink()		

	@api.model
	def create(self, vals):	
		new_record = super(sale_order_customized, self).create(vals)
		self.delete_zero_products()
		return new_record

	# @api.model
	# def create(self, vals):	
	# 	new_record = super(sale_order_customized, self).create(vals)
	# 	self.delete_zero_products()
	# 	return new_record

	@api.multi
	def write(self, vals):
		res =super(sale_order_customized, self).write(vals)
		self.delete_zero_products()
		return res
	def delete_zero_products(self):
		for lines in self.instant_promo:
			if lines.qty == 0:
				lines.unlink()

	@api.onchange('partner_id')
	def get_due_ammount(self):
		all_records = self.env['account.invoice'].search([('state','=',"open")])
		total_30  = 0
		total_60  = 0
		total_90  = 0
		total_120 = 0
		if self.partner_id:
			for x in all_records:
				if x.partner_id == self.partner_id:
					if x.due_days <=30:
						total_30 = total_30 + x.amount_total
					elif x.due_days <=60:
						total_60 = total_60 + x.amount_total
					elif x.due_days <=90:
						total_90 = total_90 + x.amount_total	
					else:
						total_120 = total_120 + x.amount_total	
			self.due = str(total_30) + "  (30 Days)       " + str(total_60) + "  (60 Days)       " +  str(total_90) + "  (90 Days)      " + str(total_120) + "  (120 Days)   " 

	@api.multi
	def action_confirm(self):
		for lines in self.instant_promo:
			self.order_line.create({
				'product_id': lines.product_id.id,
				'product_uom_qty':lines.qty,
				'price_unit': 0,
				'order_id':self.id
				})
		return  super(sale_order_customized,self).action_confirm()

	@api.constrains('order_line')
	def check_product_repeatetion(self):
		items= []
		flag = 0
		if self.product_id:
			for x in self.order_line:
				items.append(x.product_id.id)
		counter=collections.Counter(items)
		for x in counter.values():
			if x > 1:
				flag = 1
		if flag == 1:
			raise ValidationError('Same Product exists multiple times in Sale Order')

	@api.onchange('order_line')
	def on_change_instant_promo(self):
		
		items= []
		flag = 0
		if self.product_id:
			for x in self.order_line:
				items.append(x.product_id.id)
		counter=collections.Counter(items)
		for x in counter.values():
			if x > 1:
				flag = 1
		if flag == 1:
			raise ValidationError('Same Product exists multiple times in Sale Order')
		else:
			instant_promo_lines = self.env['promo.instant'].search([('sales_promo_id5.scheme_from_dt','<=',self.date_order), ('sales_promo_id5.scheme_to_dt','>=',self.date_order), ('sales_promo_id5.stages','=',"validate")])
			sale_order_lines = self.env['sale.order.line'].search([])
			for x in self.order_line:
				for y in instant_promo_lines:
					if x.product_id.id == y.product.id and x.order_id.partner_id in y.sales_promo_id5.customer:
						invoice_lines = self.env['account.invoice.line'].search([('invoice_id.date','>=',y.sales_promo_id5.scheme_from_dt), ('invoice_id.date','<=',y.sales_promo_id5.scheme_to_dt),('product_id.id','=',y.product.id),('invoice_id.partner_id.id','=',self.partner_id.id),('invoice_id.state','!=',"draft")])
						current_quantity = 0
						for qt in self.order_line:
							if qt.product_id.id == y.product.id and qt.price_unit != 0:
								current_quantity = current_quantity + qt.product_uom_qty
						invoice_total = (self.quantity(invoice_lines)[0] - self.quantity(invoice_lines)[2]) + current_quantity
						invoice_total_promo =  self.quantity(invoice_lines)[1] - self.quantity(invoice_lines)[3]
						reward_quantity = (int(invoice_total/y.qty) * y.qty_reward) - invoice_total_promo
						ids = []
						for a in self.instant_promo:
							ids.append(a.product_id.id)
						if x.product_id.id not in ids and reward_quantity > 0:
							self.instant_promo |= self.instant_promo.new({'product_id':x.product_id.id,'qty': reward_quantity,'instant_promo_id': self.id,'manual':True})
						elif x.product_id.id in ids:
							for c in self.instant_promo:
								if c.product_id.id == x.product_id.id:
									if c.manual == True:
										c.qty = reward_quantity

			product_lst = []
			for y in self.order_line:
				product_lst.append(y.product_id.id)
			for lines in self.instant_promo:
				if lines.product_id.id not in product_lst:
					if lines.manual == True:
						lines.qty = 0
			# for x in self.order_line:
			# 	if x.product_id.pcs_per_carton > 0:
			# 		print x.product_id.pcs_per_carton
			# 		print x.product_uom_qty
			# 		print x.carton
			# 		print "llllllllllllllllll"
			# 		print "llllllllllllllllll"
			# 		x.carton = x.product_uom_qty / x.product_id.pcs_per_carton
			# 		print x.carton

	def _prepare_instant_promo(self, product_id, qty, id):
		data = {
		'product_id':product_id,
		'qty': qty,
		'instant_promo_id': id,

		}
		return data

	
	def quantity(self,invoice):
		total_quantity = [0,0,0,0]
		for z in invoice:
			if z.invoice_id.type == "out_invoice":
				if z.price_unit != 0:
					total_quantity[0] = total_quantity[0] + z.quantity
				else:
					total_quantity[1] = total_quantity[1] + z.quantity
			elif z.invoice_id.type == "out_refund":
				if z.price_unit != 0:
					total_quantity[2] = total_quantity[2] + z.quantity
				else:
					total_quantity[3] = total_quantity[3] + z.quantity
		return total_quantity



################################################################################
#**************************************##**************************************#
#---------------------Sale Order Line -----------------------------------------#
#**************************************##**************************************#
################################################################################
class sale_order_line_extension(models.Model):
	_inherit = "sale.order.line"

	uom 			= fields.Char(string="UOM")
	carton 			= fields.Float(string="Quantity (CARTONS)")
	last_sale 		= fields.Float(string="Last Sale")  
	promo_code 		= fields.Many2one('naseem.sales.promo',string="PROMO CODE",readonly=True)
	customer_price 	= fields.Float(string="Net Price")
	pricelist_ext 	= fields.Many2one('product.pricelist', string = "Pricelist")
	price 			= fields.Many2one('product.pricelist.item')
	check_boolean 	= fields.Boolean()
	set_list_price 	= fields.Boolean()
	# price_check 	= fields.Boolean()
	check_promo 	= fields.Boolean(string="Promo ?", default=False)
	trial_price_unit 	= fields.Float(string="local Price")
	
	


	@api.onchange('product_id')
	def check_pricelist_lastSale_Promo(self):
########################################
#       checking Pricelist
########################################
		if self.product_id:
			# self.price_unit = self.product_id.list_price_own
			self.uom = self.product_id.uom
			pricelist = self.env['product.pricelist'].search([('id','=',self.order_id.partner_id.linked_pricelist.id)])
			pricelist_lines = self.env['product.pricelist.item'].search([('pricelist_id','=',pricelist.id)])
			promoList = self.env['promo.customer'].search([('customer','=',self.order_id.partner_id.id),('stages','=',"confirm")])
			promoWizard = self.env['naseem.sales.promo'].search([])
			
			for x in pricelist_lines:
				if x.product_id.id == self.product_id.id or x.categ_id.id == self.product_id.categ_id.id:
					self.pricelist_ext = self.order_id.partner_id.linked_pricelist.id
					self.check_boolean = True
			

			for x in promoList:
				if x.promotion.applicable_on == "product": 
					if x.promotion.scheme_application == "list_price" and x.promotion.prod_name == self.product_id :
						self.set_list_price = True
						self.pricelist_ext = 2 
					else:
						self.set_list_price = False
				elif x.promotion.applicable_on == "category":
					if x.promotion.scheme_application == "list_price" and x.promotion.prod_cat == self.product_id.categ_id:
						self.set_list_price = True
						self.pricelist_ext = 2 
					else:
						self.set_list_price = False
			all_records = self.env['account.invoice'].search([])
			all_promotions = self.env['naseem.sales.promo'].search([])

########################################
#       Checking Invoice
########################################

			for a in all_promotions:
				if self.product_id == a.prod_name:
					self.promo_code = a.id
					self.check_promo = True
				else:
					self.promo_code = False
					self.check_promo = False

########################################
#       Last Sale Price
########################################

			for x in all_records:
				if self.order_id.partner_id == x.partner_id:	
					for y in x.invoice_line_ids:
						if self.product_id == y.product_id:
							self.last_sale = y.customer_price

			if self.product_id.pcs_per_carton > 0:
				self.carton = self.product_uom_qty / self.product_id.pcs_per_carton
				return



	@api.onchange('discount','price_unit')
	def calculate_customer_price(self):
		# if self.discount:
		discounted_amount = (self.price_unit/100)*self.discount
		self.customer_price = self.price_unit - discounted_amount
		print self.price_unit
		print self.customer_price
		# if self.check_boolean == False:
		# 	if self.price_unit != self.trial_price_unit:
		# 		self.price = ""

	@api.onchange('product_uom_qty')
	def get_cartons(self):
		if self.product_uom_qty and self.product_id:
			self.product_uom_qty = round(self.product_uom_qty)
			self.carton = self.product_uom_qty / self.product_id.pcs_per_carton

	# @api.onchange('carton')
	# def get_quantity(self):
	# 	if self.carton and self.product_id:
	# 		self.product_uom_qty = self.carton * self.product_id.pcs_per_carton

	@api.onchange('price')
	def get_price(self):
		self.pricelist_ext = self.price.pricelist_id.id


	@api.onchange('carton')
	def get_pieces(self):
		if self.carton:
			self.product_uom_qty = self.carton * self.product_id.pcs_per_carton


	@api.onchange('product_id','product_uom_qty','customer_price','pricelist_ext')
	def _onchange_product_line(self):
		if self.product_id and self.pricelist_ext:
			for item in self.pricelist_ext.item_ids:
				if item.product_id.id == self.product_id.id:
					if item.compute_price == 'fixed':
						if item.fixed_price != 0.0:
							self.price_unit = item.fixed_price
					elif item.compute_price == 'formula':
						if item.price_discount != 0.0:
							self.price_unit = self.product_id.with_context(pricelist=item.base_pricelist_id.id).price
							self.discount = item.price_discount

					else:
						raise Warning('Pls select compute price to fix or formula in the pricelist.')

	@api.onchange('product_id')
	def check_price_new(self):
		if self.product_id:
			new = self.env['product.pricelist.item'].search([('pricelist_id.name','=','List Price'),('product_id','=',self.product_id.id)])
			if self.check_boolean == False and self.check_promo == False:
				self.price = new.id


	@api.onchange('price_unit')
	def _onchange_price(self):
		if self.price_unit != 1 and self.price_unit != self.price.fixed_price:
			self.price = False

class sale_order_line_extension(models.Model):
	_name = "sale.approve"

	@api.multi
	def approve_backorder(self):
		active_class = self.env['sale.order'].browse(self._context.get('active_id'))
		if active_class:
			if active_class.direct_invoice_check == True:
				active_class.state2 = "complete"
			else:
				active_class.state = "complete"
			back_order = self.env['stock.picking'].search([('origin','=',active_class.name),('state','not in',('done','cancel'))])
			print back_order
			print "kkkkkkkkkkkkkkkkkkkkkkkkkkkkk"
			if back_order:
				print "Found"
				print "xxxxXXXxxxXXXXxxxxxxxxxxx"
				back_order.state = "cancel"



# ==========================================================


	# @api.multi
	# def _get_display_price(self, product):
	#    if self.order_id.pricelist_id.discount_policy == 'without_discount':
	# 	  from_currency = self.order_id.company_id.currency_id
	# 	  return from_currency.compute(product.lst_price, self.pricelist_ext.currency_id)
	#    return product.with_context(pricelist=self.pricelist_ext.id).price

	# @api.multi
	# @api.onchange('product_id','pricelist_ext')
	# def product_id_change(self):
	# 	if not self.product_id:
	# 		return {'domain': {'product_uom': []}}

	# 	vals = {}
	# 	domain = {'product_uom': [('category_id', '=', self.product_id.uom_id.category_id.id)]}
	# 	if not self.product_uom or (self.product_id.uom_id.id != self.product_uom.id):
	# 		vals['product_uom'] = self.product_id.uom_id
	# 		vals['product_uom_qty'] = 1.0

	# 	product = self.product_id.with_context(
	# 		lang=self.order_id.partner_id.lang,
	# 		partner=self.order_id.partner_id.id,
	# 		quantity=vals.get('product_uom_qty') or self.product_uom_qty,
	# 		date=self.order_id.date_order,
	# 		pricelist=self.pricelist_ext.id,
	# 		uom=self.product_uom.id
	# 		)
	# 	name = product.name_get()[0][1]
	# 	if product.description_sale:
	# 		name += '\n' + product.description_sale
	# 	vals['name'] = name

	# 	self._compute_tax_id()

	# 	if self.pricelist_ext and self.order_id.partner_id:
	# 		vals['price_unit'] = self.env['account.tax']._fix_tax_included_price(self._get_display_price(product), product.taxes_id, self.tax_id)
	# 		vals['trial_price_unit'] = vals['price_unit']
	# 	self.update(vals)

	# 	title = False
	# 	message = False
	# 	warning = {}
	# 	if product.sale_line_warn != 'no-message':
	# 		title = _("Warning for %s") % product.name
	# 		message = product.sale_line_warn_msg
	# 		warning['title'] = title
	# 		warning['message'] = message
	# 		if product.sale_line_warn == 'block':
	# 			self.product_id = False
	# 		return {'warning': warning}
	# 	return {'domain': domain}
	


