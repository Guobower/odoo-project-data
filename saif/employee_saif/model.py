# -*- coding: utf-8 -*- 
import psycopg2


from odoo import models, fields, api

class MB_Project_Extension(models.Model):
	_inherit = 'hr.employee'

	f_name = fields.Char("Father Name")
	cnic = fields.Char("CNIC")
	religion = fields.Char("Religion")
	doj = fields.Date("D.O.J")
	e_contact = fields.Char("Contact")
	per_address = fields.Text("Permanent Address")
	tem_address = fields.Text("Temporary Address")
	emp_link = fields.One2many('ext.employee','emp_filed')


	@api.multi
	def data_base(self):
		try:
			conn = psycopg2.connect("dbname='logistic_vision' user='postgres' host='localhost' password='postgres'")
		except:
			print "I am unable to connect to the database"
		cur = conn.cursor()
		cur.execute(""" SELECT * FROM account_invoice""")
		result = cur.fetchall()
		print result
		print "-------------------------------------------------9"
		cr = self.env.cr
		cr.execute(""" SELECT * FROM account_invoice""")
		# cr.execute(""" select * from nayyab_Inspiron_N4050.logistic_vision.dbo.account_invoice""")
		result = cr.fetchall()
		print result
		print "kkkkkkkkkkkkkkkkkkkkkk"


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
	








