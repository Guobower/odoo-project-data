from odoo import models, fields, api

class summary_ffc(models.Model):
	_name = 'summary.ffc'
	_rec_name = 'name'

	name          		= fields.Char(compute = '_computed_field')
	Customer 			= fields.Many2one('res.partner',string="Customer",required=True)
	Branch 				= fields.Many2one('branch',string="Branch")
	amt_total 			= fields.Float(string="Amount Total")
	invoice_date 		= fields.Date(string="Bill Date",required=True)
	date_from 			= fields.Date()
	date_to 			= fields.Date()
	got 			    = fields.Boolean()
	mir 			    = fields.Boolean()
	dar 			    = fields.Boolean()
	inv_no 				= fields.Char(string="Invoice No P")
	inv_no1 			= fields.Char(string="Invoice No S")
	bill_no 			= fields.Many2one('bill.no',string="Bill No")
	pun_fuel_deduct 	= fields.Float(string="Punjab Fuel Deduction")
	sin_fuel_deduct 	= fields.Float(string="Sindh Fuel Deduction")
	m_tons_punjab 		= fields.Char(string="M Tons Punjab")
	m_tons_sindh 		= fields.Char(string="M Tons Sindh")
	pun_num 			= fields.Char(string="P-GST-NO.")
	sin_num 			= fields.Char(string="S.GST.NO.")
	val_excl_punjab_st  = fields.Float(string="Value Excl Punjab S.T")
	val_excl_sindh_st   = fields.Float(string="Value Excl Sindh S.T")
	pun_invoice 		= fields.Many2one('account.invoice',string="Punjab Invoice")
	sin_invoice 		= fields.Many2one('account.invoice',string="Sindh Invoice")
	invoice_link 		= fields.Many2one('account.invoice',string="Invoice Link")
	sum_ids 			= fields.One2many('summary.tree','sum_id')
	sum_ids2 			= fields.One2many('ufc.auto','ufc_summary')
	value_ids 			= fields.One2many('ufc.auto','ufc_dharki')
	stages    			= fields.Selection([
        				('draft', 'Draft'),
        				('update', 'Updated'),
        				('validate', 'Validate'),
        				],default='draft')

# ==============================giving rec name by computed function =======================
# ==============================giving rec name by computed function =======================

	@api.depends('Customer')
	def _computed_field(self):
		if self.Customer:
			self.name = "Summary of "+str(self.Customer.name)


	@api.multi
	def draft(self):
		self.stages = "draft"


	@api.onchange('Customer')
	def get_branch(self):
		users = self.env['res.users'].search([('id','=',self._uid)])
		if self.Customer:
			self.Branch = users.Branch.id
		if self.Customer.name == "FFC Goth Machi":
			self.got = True
			self.mir = False
			self.dar = False
		if self.Customer.name == "FFC Mir Pur Mathelo":
			self.got = False
			self.mir = True
			self.dar = False
		if self.Customer.name == "Engro Fertilizer Dharki":
			self.got = False
			self.mir = False
			self.dar = True





# ===========================updating invoice already created on generate button==============
# ===========================updating invoice already created on generate button==============

	@api.multi
	def validate(self):
		self.stages = "validate"
		if self.Customer:
			if self.pun_invoice and self.sin_invoice:
				# records = self.env['account.invoice'].search([('summary_id','=',self.id)])
				if self.Customer.name== "FFC Goth Machi" or self.Customer.name== "FFC Mir Pur Mathelo":

					for data in self.pun_invoice:
						if data.province == "Punjab":
							data.partner_id = self.Customer.id
							data.date_invoice = self.invoice_date
							data.bill_no = self.bill_no.name
							data.province = "Punjab"
							data.branch = self.Branch.id
							data.m_tons = self.m_tons_punjab
							data.invoice_line_ids.name = "Value Excl Punjab S.T"
							data.invoice_line_ids.price_unit = self.val_excl_punjab_st
					for data in self.sin_invoice:
						if data.province == "Sindh":
							data.partner_id = self.Customer.id
							data.date_invoice = self.invoice_date
							data.bill_no = self.bill_no.name
							data.province = "Sindh"
							data.branch = self.Branch.id
							data.m_tons = self.m_tons_sindh
							data.invoice_line_ids.name = "Value Excl Punjab S.T"
							data.invoice_line_ids.price_unit = self.val_excl_sindh_st
			
			if self.invoice_link:

				for data in self.invoice_link:
				
					data.partner_id = self.Customer.id
					data.date_invoice = self.invoice_date
					data.bill_no = self.bill_no.name
					data.branch = self.Branch.id
					data.invoice_line_ids.name = "Company Price"
					data.invoice_line_ids.price_unit = self.amt_total


		if not self.pun_invoice and not self.sin_invoice:
			if self.Customer.name== "FFC Goth Machi" or self.Customer.name== "FFC Mir Pur Mathelo":

				records = self.env['account.invoice'].create({
					'partner_id':self.Customer.id,
					'date_invoice':self.invoice_date,
					'bill_no':self.bill_no.name,
					'province':"Punjab",
					'branch':self.Branch.id,
					'm_tons': self.m_tons_punjab,
					# 'summary_id': self.id

					})

				self.pun_invoice = records.id

				records.invoice_line_ids.create({
					'name':"Value Excl Punjab S.T",
					'price_unit':self.val_excl_punjab_st,
					'account_id':17,
					'quantity':1,
					'invoice_id' : records.id

					})

				records_sin = self.env['account.invoice'].create({
					'partner_id':self.Customer.id,
					'date_invoice':self.invoice_date,
					'bill_no':self.bill_no.name,
					'province':"Sindh",
					'branch':self.Branch.id,
					'm_tons': self.m_tons_sindh,
					# 'summary_id': self.id
					})

				self.sin_invoice = records_sin.id

				records_sin.invoice_line_ids.create({
					'name':"Value Excl Sindh S.T",
					'price_unit':self.val_excl_sindh_st,
					'account_id':17,
					'quantity':1,
					'invoice_id' : records_sin.id

					})

		if not self.invoice_link:
			if self.Customer.name != "FFC Goth Machi" and self.Customer.name != "FFC Mir Pur Mathelo":

				data = self.env['account.invoice'].create({
					'partner_id':self.Customer.id,
					'date_invoice':self.invoice_date,
					'bill_no':self.bill_no.name,
					'branch':self.Branch.id,
					# 'summary_id': self.id

					})

				self.invoice_link = data.id

				data.invoice_line_ids.create({
					'name':"Company Price",
					'price_unit':self.amt_total,
					'account_id':17,
					'quantity':1,
					'invoice_id' : data.id

					})

		
					

# ===================creating Customer invoice on generate button from bill summary===========			
# ===================creating Customer invoice on generate button from bill summary===========			


	@api.multi
	def generate(self):

		self.stages = 'update'

		for x in self.sum_ids:
			if x.sum_id.id == self.id:
				x.unlink()

		if self.Customer.name == "FFC Goth Machi":
			records = self.env['ufc.auto'].search([('customer.id','=',self.Customer.id),('bill_date','=',self.invoice_date),('Bill_No','=',self.bill_no.id),('remaining','=',0)])
		if self.Customer.name == "FFC Mir Pur Mathelo":
			records = self.env['ufc.auto'].search([('customer.id','=',self.Customer.id),('bill_date','=',self.invoice_date),('remaining','=',0)])
		if self.Customer.name == "Engro Fertilizer Dharki":
			records = self.env['ufc.auto'].search([('customer.id','=',self.Customer.id),('Bill_No','=',self.bill_no.id)])
			
		entries = []
		for x in records:
			if x.region.code not in entries:
				entries.append(x.region.code)


	# for line in records:
	# 	line.Bill_No = self.bill_no


		def get_amt():
			active_ids = []
			grand_tot = 0
			for x in entries:
				del active_ids[:]
				for y in records:
					if y.region.code == x:
						active_ids.append(y)
				amount = 0
				for b in active_ids:
					amount = amount + b.sale_price
				grand_tot = grand_tot + amount

			return grand_tot

		self.amt_total = get_amt()


		for y in records:
			y.ufc_summary = self.id

	
		for y in records:
			y.ufc_dharki = self.id

		active_ids = []
		grand_tot = 0
		for x in entries:

			del active_ids[:]

			for y in records:
				if y.region.code == x:
					active_ids.append(y)

			number_of_records = len(active_ids)/10
			sheets = number_of_records
			if number_of_records < 1:
				sheets = 1

			weight = 0
			for a in active_ids:
				weight = weight + int(a.weight)

			amount = 0
			for b in active_ids:
				amount = amount + b.sale_price

			grand_tot = grand_tot + amount

			region = ""
			for z in active_ids:
				region = z.region.name


			create_records = self.env['summary.tree'].create({
				'Region': x,
				'region_name': region,
				'sum_id': self.id,
				'Sheet': sheets,
				'M_tons': weight,
				'Amount': amount
			})

# =========================creating models and tree view required for bill summary===========
# =========================creating models and tree view required for bill summary===========

class summary_tree(models.Model):
	_name = 'summary.tree'

	Region 		= fields.Char()
	bill_num     = fields.Char(string="Bill No")
	region_name = fields.Char(string="Region Name")
	Sheet 		= fields.Char()
	M_tons 		= fields.Char(string="M Tons")
	Amount 		= fields.Char()
	Remarks 	= fields.Char()
	sum_id 		= fields.Many2one('summary.ffc')


class ufc_auto_tree(models.Model):
	_inherit = 'ufc.auto'

	ufc_summary = fields.Many2one('summary.ffc')
	ufc_dharki = fields.Many2one('summary.ffc')
