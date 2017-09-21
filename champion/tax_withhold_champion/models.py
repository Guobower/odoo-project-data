from odoo import models, fields, api

class TaxWithold(models.Model):
	_name = 'tax.withold'

	supplier       = fields.Char(string="Supplier")
	date           = fields.Date(string="Date")
	amount         = fields.Integer(string="Amount")
	tax            = fields.Float(string="Tax Withheld")
	tax_name       = fields.Many2one('account.tax',string="Tax Name")
	challan_no     = fields.Char(string="Challan No.")