from odoo import models, fields, api

class TaxWork(models.Model):
	_name = 'taxes.work'

	date_from       = fields.Date(string="Date From")
	date_to         = fields.Date(string="Date To")
	sum_id     = fields.One2many('tax.tree','tax_id')
	
	@api.multi
	def generate_suppliers(self):
		all_suppliers 	= self.env['res.partner'].search([('supplier','=',True)])
		journal_ent 	= self.env['account.move'].search([])
		line 			= self.env['tax.tree'].search([])
		credit_amount = 0 
		debit_amount = 0
		total_payment = 0
		total_tax = 0
		if self.date_from and self.date_to:
			for x in all_suppliers:
				credit_amount = 0 
				debit_amount  = 0
				total_payment = 0
				total_tax = 0
				for y in journal_ent:
					for z in y.line_ids:
						if x.name == z.partner_id.name:
							if z.date >= self.date_from and z.date <= self.date_to:
								if z.debit > 0:
									debit_amount = debit_amount + z.debit
								elif z.credit > 0:
									credit_amount = credit_amount +z.credit
				if credit_amount > 0 or debit_amount > 0 or total_payment >0:	
					customer_payments = self.env['customer.payment.bcube'].search([('partner_id','=',x.id)])
					for a in customer_payments:
						total_payment = total_payment + a.amount
						total_tax = total_tax + a.t_total
					create_line = line.create({
						'suppliers' : x.name,
						'open_bal' : debit_amount + credit_amount,
						'sales' : debit_amount,
						'payment' : total_payment,
						'tax_appl' : total_tax,
						'tax_dedt' : total_tax,
						'tax_paid' : total_tax,
						'close_bal' : debit_amount + credit_amount + debit_amount - total_payment,
						'tax_id' : self.id,
						})
				
				# print "Vendor Name"
				# print x.name
				# print "Debit Amount"
				# print debit_amount
				# print "Credit Amount"
				# print credit_amount
				# print "Total Payment Made"
				# print total_payment
		


class TaxTree(models.Model):
	_name = "tax.tree"

	suppliers  = fields.Char(string="Supplier")
	open_bal   = fields.Char(string="Opening Balance")
	sales      = fields.Char(string="Sales")
	payment    = fields.Char(string="Payment")
	tax_appl   = fields.Char(string="Tax Applicable")
	tax_dedt   = fields.Char(string="Tax Deducted")
	tax_paid   = fields.Char(string="Tax Paid")
	close_bal  = fields.Char(string="Closing Balance")
	tax_id     = fields.Many2one('taxes.work')


