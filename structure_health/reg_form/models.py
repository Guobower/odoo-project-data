# -*- coding: utf-8 -*-
import re
from odoo.exceptions import Warning, ValidationError
from openerp import models, fields, api
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta


class RegForm(models.Model):
	_name = 'reg.form'

	package = fields.Many2one('reg.package', string="PACKAGE", required=True)
	service = fields.Many2many('struct.service', string="Service", required=True)
	branch = fields.Many2one('branch', string="BRANCH")
	status = fields.Many2one('reg.status', string="Status")
	current_trainer = fields.Many2one('hr.employee', string="Current Trainer")
	joining = fields.Date(string="JOINING")
	rejoining = fields.Date(string="RE JOINING")
	expire_date = fields.Date(string="EXPIRY DATE")
	monthly = fields.Float(string="MONTHLY")
	ref_no = fields.Char(string="REF. NO")
	assesment = fields.Char(string="ASSESSMENT")
	total = fields.Float(string="TOTAL")
	discount_type = fields.Selection([('per', 'Percentage'), ('amt', 'Amount')], string="Discount Type")
	gender = fields.Selection([('male', 'Male'), ('female', 'Female'),('other', 'Other')], string="Gender")
	trainer = fields.Selection([('self', 'Self'), ('trainer', 'Trainer')], string="Trainer")
	discount = fields.Integer(string="Discount")
	discount_amt = fields.Float(string="Discounted Amount")
	advance = fields.Char(string="ADVANCE")
	balance = fields.Char(string="BALANCE")
	name = fields.Char(string="FULL NAME", required=True)
	dob = fields.Date(string="DATE OF BIRTH")
	cnic = fields.Char(string="CNIC#")
	profession = fields.Char(string="PROFESSION")
	organization = fields.Char(string="ORGANIZATION")
	job_title = fields.Char(string="JOB TITLE")
	home_addres = fields.Char(string="HOME ADDRESS")
	office_addres = fields.Char(string="OFFICE ADDRESS")
	tel_office = fields.Char(string="TEL")
	tel_home = fields.Char(string="TEL")
	mob = fields.Char(string="MOBILE")
	email = fields.Char(string="EMAIL")
	ntn = fields.Char(string="NTN")
	sms = fields.Boolean(string="SMS")
	morning = fields.Boolean(string="MORNING")
	noon = fields.Boolean(string="NOON")
	afternoon = fields.Boolean(string="AFTERNOON")
	evening = fields.Boolean(string="EVENING")
	bol_email = fields.Boolean(string="EMAIL")
	ref_name = fields.Char(string="NAME")
	ref_contact = fields.Char(string="CONTACT")
	ref_addres = fields.Char(string="ADDRESS")
	ref_realtion = fields.Char(string="RELATIONSHIP")
	ref_name_1 = fields.Char(string="NAME")
	ref_contact_1 = fields.Char(string="CONTACT")
	ref_addres_1 = fields.Char(string="ADDRESS")
	ref_realtion_1 = fields.Char(string="RELATIONSHIP")
	bmi = fields.Char(string="I.BMI")
	weight = fields.Char(string="II.WEIGHT")
	fat = fields.Char(string="III.FAT%")
	emg_name = fields.Char(string="NAME")
	emg_contact = fields.Char(string="CONTACT")
	emg_addres = fields.Char(string="ADDRESS")
	emg_name_1 = fields.Char(string="NAME")
	emg_contact_1 = fields.Char(string="CONTACT")
	emg_addres_1 = fields.Char(string="ADDRESS")
	stages = fields.Selection([
		('leads', 'Leads'),
		('app_form', 'Application Form'),
		('member', 'Member'),
		('non_member', 'Non Active Members'),
	], default='leads')

	m_time = fields.Selection([
		('79', '7 AM - 9 AM'),
		('911', '9 AM - 11 AM'),
	], string="MORNING Times")

	n_time = fields.Selection([
		('111', '11 AM - 1 PM'),
		('13', '1 PM - 3 PM'),
	], string="NOON Times")

	a_time = fields.Selection([
		('35', '3 PM - 5 PM'),
	], string="AFTERNOON Times")

	e_time = fields.Selection([
		('57', '5 PM - 7 PM'),
		('79', '7 PM - 9 PM'),
		('910', '9 PM - 10 PM'),
	], string="EVENING Times")

	memship_no = fields.Many2one('member.ship',string="Membership No")
	seq_id = fields.Char(string="Id",readonly=True)
	member_link = fields.Many2one('res.partner', string="Member Link")
	invoice_link = fields.Many2one('account.invoice')
	payment_terms = fields.Many2one('account.payment.term', string="Payment Terms", required=True)

	@api.model
	def create(self, vals):
		vals['seq_id'] = self.env['ir.sequence'].next_by_code('mem.seq')
		new_record = super(RegForm, self).create(vals)

		return new_record

	def create_member(self):
		self.stages = 'member'
		member_entries = self.env['res.partner'].search([('id', '=', self.member_link.id)])
		if not member_entries:
			create_member_entry = member_entries.create({
				'name': self.name,
			})
			self.member_link = create_member_entry.id

	@api.multi
	def create_invoice(self):
		if re.findall('([0-9]+)', self.payment_terms.name):
			x = int(re.findall('([0-9]+)', self.payment_terms.name)[0])
		else:
			x = 0

		if self.invoice_link:
			self.invoice_link.partner_id = self.member_link.id
			self.invoice_link.status = self.status.id
			self.invoice_link.payment_term_id = self.payment_terms.id
			self.invoice_link.due_date = ''
			self.invoice_link.due_date = (datetime.now() + timedelta(days=x))
			self.invoice_link.date_invoice = ''
			self.invoice_link.date_invoice = datetime.now()
			self.invoice_link.type = 'out_invoice'

			self.invoice_link.invoice_line_ids.unlink()
			b = self.invoice_link.invoice_line_ids.create({
				'price_unit': self.package.reg_fee,
				'account_id': 27,
				'name': 'Membership Fee',
				'invoice_id': self.invoice_link.id,
			})

			for x in self.service:
				for y in self.package.pakg_tree:
					if x.name == y.service.name:
						a = self.invoice_link.invoice_line_ids.create({
							'price_unit': y.amount,
							'account_id': 27,
							'name': y.service.name,
							'invoice_id': self.invoice_link.id,
						})
			if self.discount_type == 'amt' and self.discount:
				c = self.invoice_link.invoice_line_ids.create({
					'price_unit': (self.discount) * -1.0,
					'account_id': 27,
					'name': 'Discount',
					'invoice_id': self.invoice_link.id,
				})

			if self.discount_type == 'per' and self.discount:
				d = self.invoice_link.invoice_line_ids.create({
					'price_unit': (self.total - self.discount_amt) * -1.0,
					'account_id': 27,
					'name': str(self.discount) + ' Discount',
					'invoice_id': self.invoice_link.id,
				})

		else:
			if self.stages == 'member':
				invoice_entries = self.env['account.invoice'].search([])
				create_invoice_entry = invoice_entries.create({
					'partner_id': self.member_link.id,
					'status': self.status.id,
					'payment_term_id': self.payment_terms.id,
					'due_date': datetime.now() + timedelta(days=x),
					'date_invoice': datetime.now(),
					'type': 'out_invoice',
				})

				b = create_invoice_entry.invoice_line_ids.create({
					'price_unit': self.package.reg_fee,
					'account_id': 28,
					'name': 'Membership Fee',
					'invoice_id': create_invoice_entry.id,
				})

				for x in self.service:
					for y in self.package.pakg_tree:
						if x.name == y.service.name:
							a = create_invoice_entry.invoice_line_ids.create({
								'price_unit': y.amount,
								'account_id': 27,
								'name': y.service.name,
								'invoice_id': create_invoice_entry.id,
							})

					if self.discount_type == 'amt' and self.discount:
						c = create_invoice_entry.invoice_line_ids.create({
							'price_unit': (self.discount) * -1.0,
							'account_id': 27,
							'name': 'Discount',
							'invoice_id': create_invoice_entry.id,
						})

					if self.discount_type == 'per' and self.discount:
						d = create_invoice_entry.invoice_line_ids.create({
							'price_unit': (self.total - self.discount_amt) * -1.0,
							'account_id': 27,
							'name': str(self.discount) + ' Discount',
							'invoice_id': create_invoice_entry.id,
						})

				self.invoice_link = create_invoice_entry.id

	@api.onchange('morning')
	def select_one(self):
		if self.morning == True:
			self.noon = False
			self.afternoon = False
			self.evening = False

	@api.onchange('noon')
	def select_one1(self):
		if self.noon == True:
			self.morning = False
			self.afternoon = False
			self.evening = False

	@api.onchange('afternoon')
	def select_one2(self):
		if self.afternoon == True:
			self.morning = False
			self.noon = False
			self.evening = False

	@api.onchange('evening')
	def select_one3(self):
		if self.evening == True:
			self.morning = False
			self.noon = False
			self.afternoon = False

	@api.onchange('package', 'service')
	def get_total(self):
		if self.package:
			self.total = self.package.reg_fee
			for x in self.service:
				for y in self.package.pakg_tree:
					if x.name == y.service.name:
						self.total = self.total + y.amount

	@api.onchange('discount', 'total', 'discount_type')
	def get_discount(self):
		if self.discount_type and self.total > 0:
			if self.discount_type == 'amt':
				self.discount_amt = self.total - self.discount
			if self.discount_type == 'per':
				if self.discount <= 100:
					value = self.total * (self.discount / 100.0)
					self.discount_amt = self.total - value
				else:
					raise ValidationError('Discount Can not be more than 100%')

	# if self.discount_type == False:
	# 	print "1111111111111111111111111"
	# 	self.discount_amt = self.total
	# 	self.discount = 0

	@api.onchange('joining')
	def get_expiry(self):
		if self.package:
			self.expire_date = \
				(datetime.strptime(self.joining, '%Y-%m-%d') + relativedelta(months=self.package.month)).strftime(
					'%Y-%m-%d')


# class RegBranch(models.Model):
#     _name = 'reg.branch'

#     name = fields.Char(string='Name')


class RegStatus(models.Model):
	_name = 'reg.status'

	name = fields.Char(string='Name')


class RegAccount(models.Model):
	_inherit = 'account.invoice'

	branch = fields.Many2one('branch', string='Branch')
	due_date = fields.Date(string='Due Date')
	status = fields.Many2one('reg.status',string='Status')
	customer_name = fields.Char(string="Customer Name")
	discount_amt = fields.Float(string="Discounted Amount")

	@api.multi
	def reg_pay(self):
		return {'name': 'My Window', 'domain': [], 'res_model': 'customer.payment.bcube',
				'type': 'ir.actions.act_window', 'view_mode': 'form', 'view_type': 'form',
				'context': {}, 'target': 'new', }



# class move_extend(models.Model):
#     _inherit = 'account.move'

#     branch = fields.Many2one('branch.AAA', string="Branch")


class RegTrainng(models.Model):
	_name = 'struct.training'

	customer = fields.Many2one('res.partner', string="Member", required=True)
	training = fields.Many2one('training.schedule', string="Training Session")
	start_date = fields.Date(string="Start Date")
	end_date = fields.Date(string="End Date")
	trainer = fields.Many2one('hr.employee', string="Trainer")


class RegTrainngShedule(models.Model):
	_name = 'training.schedule'

	name = fields.Char(string="Name", required=True)
	responsible = fields.Many2one('hr.employee', string="Responsible")
	tree_id = fields.One2many('training.schedule.tree', 'train_id')


class RegTrainngSheduleTREE(models.Model):
	_name = 'training.schedule.tree'

	time = fields.Char(string="Time")
	activity = fields.Many2one('struct.training.activity', string="Activity")
	desc = fields.Char(string="Description")
	status = fields.Char(string="Status")
	train_id = fields.Many2one('training.schedule')


class RegActivity(models.Model):
	_name = 'struct.training.activity'

	name = fields.Char(string='Name')


class RegTrainngStatus(models.Model):
	_name = 'training.status'

	date = fields.Date(string="Date")
	trainer = fields.Many2one('hr.employee', string="Trainer")
	status_id = fields.One2many('training.status.tree', 'status_tree')


class RegTrainngStatusTree(models.Model):
	_name = 'training.status.tree'

	member_no = fields.Char(string="Membership No")
	member = fields.Many2one('reg.form', string="Member")
	types = fields.Many2one('status.type', string="Type")
	start_time = fields.Datetime(string="Start Time")
	end_time = fields.Datetime(string="End Time")
	assesment = fields.Boolean(string="Assesment")
	diet_plan = fields.Boolean(string="Diet Plan")
	status_tree = fields.Many2one('training.status')


class RegTrainngStatusType(models.Model):
	_name = 'status.type'

	name = fields.Char(string="Name")


class RegAppoint(models.Model):
	_name = 'struct.appointment'

	name = fields.Char(string='Name')
	mem_name = fields.Many2one('res.partner',string='Name')
	walkin_name = fields.Many2one('res.partner',string='Walkin Customer')
	# book_status = fields.Many2one('book.status',string='Booking Status')
	contact = fields.Char(string='Contact')
	types = fields.Selection(
		[('member', 'Member'), ('walkin', 'Walkin'), ('ref', 'Reference'), ('comp', 'Complimentory')], string="Type")
	book_status = fields.Selection(
		[('book', 'Booked'), ('avial', 'Availed'), ('cancel', 'Cancelled')], string="Booking Status")
	date = fields.Date(string='Date')
	time = fields.Datetime(string='Time')
	member_no = fields.Many2one('member.ship', string='Membership No.')
	mamsus_name = fields.Many2one('hr.employee', string='Massus Name')
	invoice_link = fields.Many2one('account.invoice', string='Invoice')
	total = fields.Float('Discounted Amount',readonly=True)
	discount = fields.Integer('Discount')
	discount_type = fields.Selection([('per', 'Percentage'), ('amt', 'Amount')], string="Discount Type")
	appoint_id = fields.One2many('struct.appointment.tree', 'appoint_tree')

	@api.onchange('discount','discount_type')
	def get_discount(self):
		if self.discount_type:
			total = 0
			if self.discount_type == 'amt':
				for x in self.appoint_id:
					total = total + x.rates
				self.total = total - self.discount
			if self.discount_type == 'per':
				for x in self.appoint_id:
					total = total + x.rates
				if self.discount <= 100:
					value = total * (self.discount / 100.0)
					self.total = total - value
				else:
					raise ValidationError('Discount Can not be more than 100%')

	@api.onchange('member_no','rejoining')
	def get_member(self):
		if self.member_no:
			if self.types == 'member':
				records = self.env['reg.form'].search([('memship_no','=',self.member_no.id)])
				self.mem_name = records.member_link.id


	@api.multi
	def create_invoice(self):
		invoice_entries = self.env['account.invoice'].search([])
		if self.types == 'member':
			create_invoice_entry = invoice_entries.create({
						'partner_id': self.mem_name.id,
						'date_invoice': self.date,
						'discount_amt': self.total,
						'type': 'out_invoice',
					})
		if self.types == 'walkin':
			create_invoice_entry = invoice_entries.create({
						'partner_id': self.walkin_name.id,
						'customer_name': self.name,
						'date_invoice': self.date,
						'discount_amt': self.total,
						'type': 'out_invoice',
					})
		for y in self.appoint_id:
			a = create_invoice_entry.invoice_line_ids.create({
				'price_unit': y.rates,
				'account_id': 27,
				'name': y.types.name,
				'invoice_id': create_invoice_entry.id,
			})

		self.invoice_link = create_invoice_entry.id


class RegMemberShip(models.Model):
	_name = 'member.ship'

	name = fields.Char(string='Name')

class RegMemberShip(models.Model):
	_name = 'book.status'

	name = fields.Char(string='Name')


class RegAppointTree(models.Model):
	_name = 'struct.appointment.tree'

	types = fields.Many2one('types.massage', string='Type')
	duration = fields.Float(string='Duration')
	rates = fields.Float(string='Rates')
	appoint_tree = fields.Many2one('struct.appointment')

	@api.onchange('types')
	def _onchange_types(self):
		if self.types:
			self.rates = self.types.rate


class RegMassage(models.Model):
	_name = 'types.massage'

	name = fields.Char(string='Name')
	rate = fields.Float(string='Rate')


class RegVisitor(models.Model):
	_name = 'struct.visitor'
	
	date = fields.Date(string='Date')
	time = fields.Datetime(string='Time')
	attend_by = fields.Many2one('hr.employee', string="Attended By")
	name = fields.Char(string='Visitor Name')
	ref = fields.Char(string='Reference')
	cmp_name = fields.Char(string='Company Name')
	designation = fields.Char(string='Designation')
	interest_lvl = fields.Integer(string='Interest Level')
	profile_lvl = fields.Integer(string='Profile Level')
	contact = fields.Integer(string='Contact Info')
	approve = fields.Many2one('hr.employee', string="Approved")
	remarks = fields.Text(string='Remarks')
	remarks_on_call = fields.Text(string='Remarks on Call to Visitors')



class RegVisitorDaily(models.Model):
	_name = 'struct.visitor.daily'

	name = fields.Char(string='Name')


class RegVisitorMonthly(models.Model):
	_name = 'struct.visitor.monthly'

	name = fields.Char(string='Name')


class RegAttend(models.Model):
	_name = 'struct.attend'

	name = fields.Char(string='Name')


class RegAttendReport(models.Model):
	_name = 'struct.attend.report'

	name = fields.Char(string='Name')


class RegJoining(models.Model):
	_name = 'struct.joining'

	name = fields.Char(string='Name')


class RegReJoining(models.Model):
	_name = 'struct.rejoining'
	_rec_name = 'membership_no'

	date = fields.Date(string='Date')
	rejoining = fields.Date(string='Date of Rejoining')
	membership_no = fields.Many2one('member.ship',string='Membership No.',required=True)
	member = fields.Many2one('res.partner',string='Member Name')
	package = fields.Many2one('reg.package',string='Package')
	invoice_link = fields.Many2one('account.invoice')
	service = fields.Many2many('struct.service',string='Service')
	stages = fields.Selection([
		('draft', 'Draft'),
		('paid', 'Paid'),
		('validate', 'Validate'),
	], default='draft')

	@api.onchange('membership_no','rejoining')
	def get_discount(self):
		if self.membership_no:
			records = self.env['reg.form'].search([('memship_no','=',self.membership_no.id)])
			self.package = records.package.id
			self.member = records.member_link.id
			self.service = records.service

	@api.multi
	def validate(self):
		if self.membership_no:
			self.stages = 'validate'
			records = self.env['reg.form'].search([('memship_no','=',self.membership_no.id)])
			records.stages = 'member'


	@api.multi
	def create_invoice(self):
		if self.invoice_link:
			self.invoice_link.partner_id = self.member.id
			self.invoice_link.date_invoice = self.date

			self.invoice_link.invoice_line_ids.unlink()
			b = self.invoice_link.invoice_line_ids.create({
				'price_unit': self.package.reg_fee,
				'account_id': 27,
				'name': 'Membership Fee',
				'invoice_id': self.invoice_link.id,
			})

			for x in self.service:
				for y in self.package.pakg_tree:
					if x.name == y.service.name:
						a = self.invoice_link.invoice_line_ids.create({
							'price_unit': y.amount,
							'account_id': 27,
							'name': y.service.name,
							'invoice_id': self.invoice_link.id,
						})

		else:
			invoice_entries = self.env['account.invoice'].search([])
			create_invoice_entry = invoice_entries.create({
									'partner_id': self.member.id,
									'date_invoice': self.date,
									'type': 'out_invoice',
								})

			b = create_invoice_entry.invoice_line_ids.create({
				'price_unit': self.package.reg_fee,
				'account_id': 28,
				'name': 'Membership Fee',
				'invoice_id': create_invoice_entry.id,
			})

			for x in self.service:
				for y in self.package.pakg_tree:
					if x.name == y.service.name:
						a = create_invoice_entry.invoice_line_ids.create({
							'price_unit': y.amount,
							'account_id': 27,
							'name': y.service.name,
							'invoice_id': create_invoice_entry.id,
						})

			self.invoice_link = create_invoice_entry.id



class RegContinue(models.Model):
	_name = 'struct.continue'

	name = fields.Char(string='Name')


class RegDisContinue(models.Model):
	_name = 'struct.discontinue'

	name = fields.Char(string='Name')


class RegPaid(models.Model):
	_name = 'struct.paid'

	name = fields.Char(string='Name')


class RegUnPaid(models.Model):
	_name = 'struct.unpaid'

	name = fields.Char(string='Name')


class RegService(models.Model):
	_name = 'struct.service'

	name = fields.Char(string='Name')


class RegPackage(models.Model):
	_name = 'reg.package'

	name = fields.Char(string='Name', required=True)
	month = fields.Integer(string='Months', required=True)
	reg_fee = fields.Float(string='Registration Fee', required=True)
	pakg_tree = fields.One2many('reg.package.tree', 'pakg_id')


class RegPackageTree(models.Model):
	_name = 'reg.package.tree'

	service = fields.Many2one('struct.service', string="Services", required=True)
	amount = fields.Float(string="Amount")
	pakg_id = fields.Many2one('reg.package')


# class RegServiceTree(models.Model):
#     _name = 'service.package'

#     name = fields.Char(string='name')

class RegTrainer(models.Model):
	_name = 'struct.trainer'

	name = fields.Char(string='Name')


class RegSlots(models.Model):
	_name = 'struct.slots'
	_rec_name = 'name'

	start_time = fields.Char(string='Start Time')
	end_time = fields.Char(string='End Time')
	name = fields.Char(string='Name')
	training = fields.Boolean(string='Training')

	@api.onchange('start_time', 'end_time')
	def time_schedule(self):
		self.name = "%s %s %s" % (self.start_time or '', " To ", self.end_time or '')


class RegBranches(models.Model):
	_name = 'struct.branches'

	name = fields.Char(string='Name')


class RegVisitorType(models.Model):
	_name = 'struct.visit.type'

	name = fields.Char(string='Name')


class employee_extend(models.Model):
	_inherit = 'hr.employee'

	massus = fields.Boolean(string="Massus")
	trainer = fields.Boolean(string="Trainer")
	branch = fields.Many2one('branch',string="Branch")


class HrEmployee(models.Model):
	_inherit = 'hr.employee'

	trainer = fields.Boolean(string='Trainier')

class PartnerExtend(models.Model):
	_inherit = 'res.partner'

	walkin = fields.Boolean(string='Walkin Customer')

	@api.onchange('walkin')
	def change(self):
		if self.walkin == True:
			self.customer = False


class struct_user_extend(models.Model):
	_inherit  = 'res.users'
	branch = fields.Many2one ('branch',string="Branch")


class branchAAA(models.Model):
	_name = 'branch'

	address = fields.Char(string="Address")
	name = fields.Char(string="Name")
	phone = fields.Char(string="Phone")
	mobile = fields.Char(string="Mobile")


class journal_extend(models.Model):
	_inherit = 'account.journal'

	branch      = fields.Many2one('branch',string="Branch")

# class bank_extend(models.Model):
#     _inherit = 'account.bank.statement'

#     branch      = fields.Many2one('branch',string="Branch")

#     @api.onchange('journal_id')
#     def get_branch(self):
#         records = self.env['account.journal'].search([('id','=',self.journal_id.id)])
#         self.branch = records.branch.id

# class bank_extend(models.Model):
#     _inherit = 'account.bank.statement.line'

#     @api.multi
#     def process_reconciliation(self,data,uid,id):
#         new_record = super(bank_extend, self).process_reconciliation(data,uid,id)
#         records = self.env['account.bank.statement'].search([('id','=',self.statement_id.id)])
#         journal_entery =  self.env['account.move'].search([], order='id desc', limit=1)
#         journal_entery.branch = records.branch.id
#         return new_record


# class move_extend(models.Model):
#     _inherit = 'account.move'

#     branch      = fields.Many2one('branch',string="Branch")


