# -*- coding: utf-8 -*-

from openerp import models, fields, api
from datetime import datetime, timedelta

class RegForm(models.Model):
    _name = 'reg.form'

    package = fields.Many2one('reg.package',string="PACKAGE",required=True)
    branch = fields.Many2one('reg.branch',string="BRANCH")
    joining = fields.Date(string="JOINING")
    monthly = fields.Float(string="MONTHLY")
    ref_no = fields.Char(string="REF. NO")
    assesment = fields.Char(string="ASSESSMENT")
    total = fields.Float(string="TOTAL")
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
        ('draft', 'Draft'),
        ('validate', 'Validate'),
        ],default='draft')


    @api.onchange('package')
    def get_total_monthly(self):
        if self.package:
            self.monthly = self.package.monthly
            self.total = self.package.total



class RegPackage(models.Model):
    _name = 'reg.package'

    name = fields.Char(string='Name')
    total = fields.Float(string='Total')
    monthly = fields.Float(string='Monthly')
    branch = fields.Many2one('reg.branch',string='Branch')


class RegBranch(models.Model):
    _name = 'reg.branch'

    name = fields.Char(string='Name')


class RegBranch(models.Model):
    _inherit = 'account.invoice'

    branch = fields.Many2one('reg.branch',string='Branch')


class move_extend(models.Model):
    _inherit = 'account.move'

    branch      = fields.Many2one('reg.branch',string="Branch")


class RegTrainng(models.Model):
    _name = 'struct.training'

    customer = fields.Many2one('res.partner',string="Member",required=True)
    training = fields.Many2one('training.schedule',string="Training")
    start_date = fields.Date(string="Start Date")
    end_date = fields.Date(string="End Date")


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

    