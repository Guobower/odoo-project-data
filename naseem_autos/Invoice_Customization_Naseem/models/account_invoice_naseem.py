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

	due_days = fields.Integer(string="Due Days")
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
	waveoff_amount 	= fields.Float(string="Discount")
	pdc_module = fields.Many2one('pdc_bcube.pdc_bcube', string="Checks And Balance")

	@api.onchange('waveoff_amount')
	def _onchange_waveoff_amount(self):
		if self.waveoff_amount:
			self.amount_total = self.amount_total - self.waveoff_amount

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
		rec = self.env['stock.picking'].search([('origin','=',self.source)])
		rec.print_do = True
		res = super(sale_invoice_customized, self).action_invoice_open()
		return res

  

	@api.multi
	@api.constrains()
	def _check_total(self,credit,credit_limit,stop):
		if stop == True:
			if credit > credit_limit:
				raise ValidationError('Amount is exceeding credit limit')

	@api.model
	def create(self, vals):
		
	  new_record = super(sale_invoice_customized, self).create(vals)
	  credit1 = new_record.partner_id.credit + new_record.amount_total
	  credit_limit1 = new_record.partner_id.credit_limit
	  stop = new_record.partner_id.stop_invoice
	  self._check_total(credit1,credit_limit1,stop)

	  return new_record

	@api.multi
	def write(self, vals):
		super(sale_invoice_customized, self).write(vals)
		credit1 = self.partner_id.credit + self.amount_total
		credit_limit1 = self.partner_id.credit_limit
		stop = self.partner_id.stop_invoice
		self._check_total(credit1,credit_limit1,stop)
		return True


class sale_invoice_line_extension(models.Model):
	_inherit = "account.invoice.line"

	uom = fields.Char(string="UOM", readonly="1")
	carton = fields.Float(string="Quantity (CARTONS)")
	last_sale = fields.Float(string="Last Sale")  
	promo_code 		= fields.Many2one('naseem.sales.promo',string="PROMO CODE",readonly=True)
	customer_price = fields.Float(string="Net Price")
	price = fields.Many2one('product.pricelist.item')
