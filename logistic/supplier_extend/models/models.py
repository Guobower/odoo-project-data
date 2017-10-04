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
	serv_type    = fields.Selection([('imp','Import'),('exp','Export')],string="Import/Export")

	bl_tree      = fields.Many2one('res.partner')

class transport_info(models.Model):
	_name = 'route.transport'
	# _rec_name   = 'company_name'

	form          = fields.Many2one('from.qoute',string="From")
	to            = fields.Many2one('to.quote',string="To")
	fleet_type    = fields.Many2one('fleet',string="Fleet Type")
	service_type  = fields.Selection([('imp','Import'),('exp','Export')],string="Service Type")
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
	_rec_name = 'sr_no'


	customer = fields.Many2one('res.partner',string="Customer",required=True)
	s_supplier = fields.Many2one('res.partner',string="Shipping Line")
	sr_no     = fields.Char(string="SR No", readonly=True)
	book_date = fields.Date(string="Booking Date")
	eta_date = fields.Date(string="ETA Date")
	etd_date = fields.Date(string="ETD Date")
	cro = fields.Integer(string="CRO")
	no_of_con = fields.Integer(string="No of Containers")
	form = fields.Many2one('from.qoute',string="Country of Origin")
	to = fields.Many2one('to.quote',string="Destination")
	sale_link = fields.Many2one('sale.order',string="Sale Order Link")
	new_link = fields.Many2one('sale.order',string="Transport Order Link")
	implink = fields.Many2one('import.logic',string="Import Link")
	explink = fields.Many2one('export.logic',string="Export Link")
	# abc_imp = fields.Many2one('import.logic', required=True, string="Check test", index=True)
	freight   = fields.Boolean(string="Freight Forwarding")
	trans   = fields.Boolean(string="Transportation")
	store   = fields.Boolean(string="Storage")
	custm   = fields.Boolean(string="Custom Clearance")
	frieght_id = fields.One2many('freight.tree','freight_tree')
	types = fields.Selection([
        ('imp','Import'),
        ('exp','Export')
        ],string="Type")
	state = fields.Selection([
			('draft', 'Draft'),
			('val', 'Validate'),
			],default='draft')

	@api.model
	def create(self, vals):
		vals['sr_no'] = self.env['ir.sequence'].next_by_code('freight.forward')
		new_record = super(FreightForwarding, self).create(vals)

		return new_record


	@api.multi
	def validate(self):
		self.state = 'val'

		prev_rec = self.env['sale.order'].search([('freight_link','=',self.id)])
		if prev_rec.state == 'sale':
			prev_rec.state = 'draft'
			prev_rec.unlink()

		records = self.env['sale.order'].create({
				'partner_id':self.customer.id,
				'suppl_name':self.s_supplier.id,
				'freight_link': self.id,
				'state': 'sale'
				})

		self.sale_link = records.id


	@api.multi
	def create_order(self):
		prev_rec = self.env['sale.order'].search([('trans_link','=',self.id)])
		for x in prev_rec:
			if x.state == 'sale':
				x.state = 'draft'
				x.unlink()
		# if not prev_rec:
		# 	value = 0 
		# 	get_id = self.env['product.template'].search([])
		# 	for x in get_id:
		# 		if x.name == "Container":
		# 			value = x.id

		for data in self.frieght_id:
			records = self.env['sale.order'].create({
				'partner_id':self.customer.id,
				'suppl_name':self.s_supplier.id,
				'trans_link':self.id,
				'state': 'sale',
				})

			self.new_link = records.id

			records.order_line.create({
				# 'product_id':value,
				'name':'Container',
				'product_uom_qty':1.0,
				'price_unit':1,
				'crt_no':data.cont_no,
				'product_uom':1,
				'order_id':records.id,
				})

	@api.multi
	def create_custm(self):

		if self.types == 'imp':
			prev_rec = self.env['import.logic'].search([('fri_id','=',self.id)])
			prev_rec.unlink()

			records = self.env['import.logic'].create({
				'customer':self.customer.id,
				'fri_id':self.id,
				})

			self.implink = records.id

		if self.types == 'exp':
			prev_rec = self.env['export.logic'].search([('fri_id','=',self.id)])
			prev_rec.unlink()

			records = self.env['export.logic'].create({
				'customer':self.customer.id,
				'fri_id':self.id,
				})

			self.explink = records.id


class FreightTree(models.Model):
	_name = 'freight.tree'

	cont_no = fields.Integer(string="Container No")
	store_charg = fields.Integer(string="Storage Charges")
	freight_charg = fields.Integer(string="Freight Charges")
	store_supp = fields.Char(string="Storage Supplier")
	cont_type = fields.Selection([('20 ft','20 ft'),('40 ft','40 ft')],string="Container Type")

	freight_tree  = fields.Many2one('freight.forward')
