# -*- coding: utf-8 -*-

from openerp import models, fields, api
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

class RegForm(models.Model):
	_name = 'reg.form'

	package = fields.Many2one('reg.package',string="PACKAGE",required=True)
	service = fields.Many2one('struct.service',string="Service",required=True)
	branch = fields.Many2one('reg.branch',string="BRANCH")
	joining = fields.Date(string="JOINING")
	expire_date = fields.Date(string="EXPIRY DATE")
	monthly = fields.Float(string="MONTHLY")
	ref_no = fields.Char(string="REF. NO")
	assesment = fields.Char(string="ASSESSMENT")
	total = fields.Float(string="TOTAL")
	discount_type = fields.Selection([('per','Percentage'),('amt','Amount')],string="Discount Type")
	discount = fields.Integer(string="Discount")
	discount_amt = fields.Float(string="Discounted Amount")
	advance = fields.Char(string="ADVANCE")
	balance = fields.Char(string="BALANCE")
	name = fields.Char(string="FULL NAME")
	dob = fields.Char(string="DATE OF BIRTH")
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
		],default='leads')

	@api.onchange('package')
	def get_total(self):
		if self.package:
			self.total = self.package.reg_fee
			for x in self.package.pakg_tree:
				self.total = self.total + x.amount

	@api.onchange('discount')
	def get_discount(self):
		if self.discount_type and self.total > 0:
			if self.discount_type == 'amt':
				self.discount_amt = self.total - self.discount
			if self.discount_type == 'per':
				value = self.total * self.discount / 100
				self.discount_amt = self.total - value

	@api.onchange('joining')
	def get_expiry(self):
		if self.package:
			self.expire_date = (datetime.strptime(self.joining,'%Y-%m-%d') + relativedelta(months=self.package.month)).strftime('%Y-%m-%d')






class RegBranch(models.Model):
	_name = 'reg.branch'

	name = fields.Char(string='Name')


class RegAccount(models.Model):
	_inherit = 'account.invoice'

	branch = fields.Many2one('reg.branch',string='Branch')


class move_extend(models.Model):
	_inherit = 'account.move'

	branch      = fields.Many2one('reg.branch',string="Branch")


class RegTrainng(models.Model):
	_name = 'struct.training'

	customer = fields.Many2one('res.partner',string="Member",required=True)
	training = fields.Many2one('training.schedule',string="Training Session")
	start_date = fields.Date(string="Start Date")
	end_date = fields.Date(string="End Date")
	trainer = fields.Many2one('hr.employee',string="Trainer")


class RegTrainngShedule(models.Model):
	_name = 'training.schedule'

	name = fields.Char(string="Name",required=True)
	responsible = fields.Many2one('hr.employee',string="Responsible")
	tree_id = fields.One2many('training.schedule.tree','train_id')


class RegTrainngSheduleTREE(models.Model):
	_name = 'training.schedule.tree'

	time = fields.Char(string="Time")
	activity = fields.Many2one('struct.training.activity',string="Activity")
	desc = fields.Char(string="Description")
	status = fields.Char(string="Status")
	train_id = fields.Many2one('training.schedule')


class RegActivity(models.Model):
	_name = 'struct.training.activity'

	name = fields.Char(string='Name')

class RegTrainngStatus(models.Model):
	_name = 'training.status'

	date = fields.Date(string="Date")
	trainer = fields.Many2one('hr.employee',string="Trainer")
	status_id = fields.One2many('training.status.tree','status_tree')


class RegTrainngStatusTree(models.Model):
	_name = 'training.status.tree'

	member_no = fields.Char(string="Membership No")
	member = fields.Many2one('reg.form',string="Member")
	types = fields.Many2one('status.type',string="Type")
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
	book_status = fields.Char(string='Booking Status')
	contact = fields.Char(string='Contact')
	types = fields.Selection([('member','Member'),('walkin','Walkin'),('ref','Reference'),('comp','Complimentory')],string="Type")
	date = fields.Date(string='Date')
	time = fields.Datetime(string='Time')
	member_no = fields.Many2one('member.ship',string='Membership No.')
	mamsus_name = fields.Many2one('hr.employee',string='Massus Name')
	appoint_id = fields.One2many('struct.appointment.tree','appoint_tree')

class RegMemberShip(models.Model):
	_name = 'member.ship'

	name = fields.Char(string='Name')


class RegAppointTree(models.Model):
	_name = 'struct.appointment.tree'

	types = fields.Many2one('types.massage',string='Type')
	duration = fields.Char(string='Duration')
	rates = fields.Float(string='Rates')
	appoint_tree = fields.Many2one('struct.appointment')


class RegMassage(models.Model):
	_name = 'types.massage'

	name = fields.Char(string='Name')


class RegVisitor(models.Model):
	_name = 'struct.visitor'

	name = fields.Char(string='Name')

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

	name = fields.Char(string='Name')

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

	name = fields.Char(string='Name',required=True)
	month = fields.Integer(string='Months',required=True)
	reg_fee = fields.Float(string='Registration Fee')
	pakg_tree = fields.One2many('reg.package.tree','pakg_id')

class RegPackageTree(models.Model):
	_name = 'reg.package.tree'

	service = fields.Many2one('struct.service',string="Services",required=True)
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

	name = fields.Char(string='Name')

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
	