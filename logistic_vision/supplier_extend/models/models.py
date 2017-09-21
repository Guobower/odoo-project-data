# -*- coding: utf-8 -*-

from odoo import models, fields, api


class AccountMoveLineInher(models.Model):
	_inherit = 'res.partner'

	route_id  = fields.One2many('route.transport','route_trans')
	bl_id     = fields.One2many('bl.tree','bl_tree')
	cont_id   = fields.One2many('bl.tree','bl_tree')
	charge_id = fields.One2many('charg.vender','charge_tree')
	brooker   = fields.Boolean(string="Broker")
	bl_num    = fields.Boolean(string="B/l Number")
	checks     = fields.Boolean(string="check")
	cont_num  = fields.Boolean(string="Cont Wise")
	bill_type = fields.Selection([('B/L Number','B/L Number'),('Container Wise','Container Wise')],string="Billing Type")
	types     = fields.Selection([('trnas','Transporter'),('freight_fwd','Freight Forwarder')],string="Type")

	@api.onchange('bill_type')
	def get_bl(self):
		if self.bill_type == "B/L Number":
			self.bl_num    = True
			self.cont_num = False

	@api.onchange('bill_type')
	def get_cont(self):
		if self.bill_type == "Container Wise":
			self.cont_num = True
			self.bl_num    = False


	@api.onchange('types')
	def get_trans(self):
		if self.types == "freight_fwd":
			self.checks = True
		else:
			self.checks = False

	
	
class BlnumberTree(models.Model):
	_name = 'bl.tree'

	charges_serv = fields.Float(string="Service Charges")
	charges_type = fields.Many2one('serv.types',string="Service Type")

	bl_tree      = fields.Many2one('res.partner')

class BlnumberTree(models.Model):
	_name = 'bl.tree'

	charges_serv = fields.Float(string="Service Charges")
	charges_type = fields.Many2one('serv.types',string="Service Type")
	cont_type    = fields.Selection([('20 ft','20 ft'),('40 ft','40 ft')],string="Container Type")

	bl_tree      = fields.Many2one('res.partner')

class transport_info(models.Model):
	_name = 'route.transport'
	# _rec_name   = 'company_name'

	form          = fields.Many2one('from.qoute',string="From")
	to            = fields.Many2one('to.quote',string="To")
	fleet_type    = fields.Many2one('fleet',string="Fleet Type")
	trans_charges = fields.Float(string="Charges")

	route_trans = fields.Many2one('res.partner')

class ChargesVender(models.Model):
	_name = 'charg.vender'

	charges_vend = fields.Float(string="Charges")
	contain_type = fields.Selection([('20 ft','20 ft'),('40 ft','40 ft')],string="Container Type")

	charge_tree  = fields.Many2one('res.partner')


class From(models.Model):
	_name = 'from.qoute'

	name = fields.Char('name')


class To(models.Model):
	_name = 'to.quote'

	name = fields.Char('name')

class Fleet(models.Model):
	_name = 'fleet'

	name = fields.Char('Fleet Type')

class AccountExtend(models.Model):
	_inherit = 'account.invoice'

	billng_type  = fields.Char(string="Billing Type")
	bill_num     = fields.Char(string="B/L Number")

class AccountTreeExtend(models.Model):
	_inherit = 'account.invoice.line'

	crt_no           = fields.Char(string="Container No.")
	service_type     = fields.Char(string="Service Type")


class Charges_service(models.Model):
	_name = 'serv.types'

	name  = fields.Char(string="Service Type")

class FreightForwarding(models.Model):
	_name = 'freight.forward'


	customer = fields.Many2one('res.partner',string="Customer")
	supplier = fields.Many2one('res.partner',string="Supplier")
	book_date = fields.Date(string="Booking Date")
	eta_date = fields.Date(string="ETA Date")
	etd_date = fields.Date(string="ETD Date")
	cro = fields.Integer(string="CRO")
	no_of_con = fields.Integer(string="No of Containers")
	form = fields.Many2one('from.qoute',string="From")
	to = fields.Many2one('to.quote',string="To")
	types = fields.Selection([
        ('imp','Import'),
        ('exp','Export')
        ],string="Tpye")
	services = fields.Selection([
        ('freight','Freight Forwarding'),
        ('trans','Transportation'),
        ('store','Storage'),
        ('custm','Custom Clearance')
        ],string="Services")
	state = fields.Selection([
			('draft', 'Draft'),
			('complete', 'Complete'),
			],default='draft')
