# -*- coding: utf-8 -*-

from odoo import models, fields, api
class saif_extension(models.Model):
	_name	='saif.extension'
	_rec_name = 'employee'

	employee 	 = fields.Many2one('hr.employee',string="Employee")
	date = fields.Date(string='Date', required=True)
	department	 = fields.Many2one('hr.department',string="Department")
	amount = fields.Float(string='Amount')
	returned = fields.Float(string='Returned')
	net = fields.Float(string='Net')
	payment_bank = fields.Boolean(string='Payment Through Bank')
	cash_book	 = fields.Many2one('account.bank.statement',string='Cash Book')
	s_bank	 = fields.Many2one('account.journal',string='Bank')
	s_counter	 = fields.Many2one('account.account',string='Counter Account')
	description	 = fields.Char(string='Description', required=True)
	e_currency	 = fields.Many2one('res.currency',string='Currency', required=True)
	proj	 = fields.Many2one('project.project',string='Project', required=True)
	saif_tree_link = fields.One2many('saif.ext.tree','part_id')
	seq = fields.Char("CE No.",readonly=True)

	@api.model 
	def create(self, vals):
		vals['seq'] = self.env['ir.sequence'].next_by_code('ch.seq')
		new_record = super(saif_extension, self).create(vals) 
		return new_record


	state = fields.Selection([
		('exp', 'Expenses'),
		('adv', 'Advance'),
		('reim', 'Reimbursement'),
		('reim_sal', 'Reimbursement Salary'),
		('arr_sal', 'Arrears Salary'),
		('arr', 'Arrears'),
		],default='exp',string ="Type")

	status = fields.Selection([
		('draft', 'Draft'),
		('val', 'Validate'),
		],default='draft')

	@api.multi
	def val(self):
		self.status = "val"

		cash_enteries = self.env['account.bank.statement'].search([('journal_id.type','=',self.cash_book.journal_id.type),('proj.id','=',self.proj.id)])
		if cash_enteries:
			for x in cash_enteries.line_ids:
				if x.ref == self.seq:
					x.unlink()

		if cash_enteries:
			inv = []
			for invo in self.saif_tree_link:
				inv.append({
					'date':invo.expense_date,
					'name':invo.expense_note,
					'partner_id':self.employee.id,
					'ref':self.seq,
					'amount':invo.expense_amount,
					'line_ids':cash_enteries.id,
					})
			
			cash_enteries.line_ids = inv
			inv=[]


	@api.multi
	def cancel(self):
		self.status = "draft"

	@api.onchange('saif_tree_link')
	def on_change_amount(self):
		if self.saif_tree_link:
			self.amount = 0.0
			for x in self.saif_tree_link:
				self.amount = self.amount + x.expense_amount


class saif_extension_tree(models.Model):
	_name='saif.ext.tree'
	expense_date = fields.Date(string='Expense Date', required=True)
	expense_note = fields.Char(string='Expense Note', required=True)
	expense_amount = fields.Float("Total Amount")
	part_id = fields.Many2one('saif.extension')



class account_bank_extension(models.Model):
	_inherit = 'account.bank.statement'

	proj	 = fields.Many2one('project.project',string='Project', required=True)
