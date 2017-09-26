# -*- coding: utf-8 -*- 
from odoo import models, fields, api

class MB_Project_Extension(models.Model):
	_inherit = 'hr.employee'

	f_name = fields.Char("Father Name")
	cnic = fields.Char("CNIC")
	religion = fields.Char("Religion")
	doj = fields.Char("D.O.J")
	e_contact = fields.Char("Contact")
	per_address = fields.Text("Permanent Address")
	tem_address = fields.Text("Temporary Address")
	emp_link = fields.One2many('ext.employee','emp_filed')


class SC_Employee_Ext(models.Model):
	_name = 'ext.employee'

	emp_filed = fields.Many2one('hr.employee')

	relation = fields.Text("Relation")
	name = fields.Char("Name")
	cnic = fields.Char("CNIC")	
	e_contact = fields.Char("Contact")
	per_address = fields.Text("Permanent Address")
	tem_address = fields.Text("Temporary Address")
	main = fields.Boolean("Main")
	








