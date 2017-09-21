#-*- coding:utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2011 OpenERP SA (<http://openerp.com>). All Rights Reserved
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from openerp import models, fields, api
import xlsxwriter

class working_161(models.AbstractModel):
	_name = 'report.161_xl_report.report_module'

	@api.model
	def render_html(self,docids, data=None):
		report_obj = self.env['report']
		report = report_obj._get_report_from_name('161_xl_report.report_module')
		records = self.env['taxes.work'].search([])

		self.summary_report(records)

		docargs = {
			'doc_ids': docids,
			'doc_model': 'taxes.work',
			'docs': records,
			'data': data,
			}

		return report_obj.render('161_xl_report.report_module', docargs)



	def summary_report(self,records):
		row = 1
		col = 0
		for line in records:
			workbook = xlsxwriter.Workbook('customer_invoices.xlsx')
			worksheet = workbook.add_worksheet()

			main_heading = workbook.add_format({
				"bold": 1,
				"align": 'center',
				"valign": 'vcenter'
				})

			main_data = workbook.add_format({
				"align": 'center',
				"valign": 'vcenter'
				})


			worksheet.set_column('A:A', 5)
			worksheet.set_column('B:E', 20)
			worksheet.set_column('F:F', 40)
			worksheet.set_column('G:J', 20)
			worksheet.set_column('K:K', 30)
			worksheet.set_column('L:L', 15)
			worksheet.set_column('M:M', 45)
			worksheet.set_column('N:O', 15)
			worksheet.set_column('P:P', 40)
			worksheet.write('A1', 'Date From',main_heading)
			worksheet.write('B1', 'Date To',main_heading)
			worksheet.write('C1', 'Supplier',main_heading)
			worksheet.write('D1', 'Opening Balance',main_heading)
			worksheet.write('E1', 'Sales',main_heading)
			worksheet.write('F1', 'Payments',main_heading)
			worksheet.write('G1', 'Tax Applicable',main_heading)
			worksheet.write('H1', 'Tax Dedected',main_heading)
			worksheet.write('I1', 'Tax Paid',main_heading)
			worksheet.write('J1', 'Closing Balance',main_heading)

		


			for x in records.sum_id:
				# worksheet.write_string (row, col,line.date_from)
				# worksheet.write_string (row, col+1,line.date_to)
				worksheet.write_string (row, col+2,x.suppliers)
				worksheet.write_string (row, col+3,x.open_bal)
				worksheet.write_string (row, col+4,x.sales)
				worksheet.write_string (row, col+5,x.payment)
				worksheet.write_string (row, col+6,x.tax_appl)
				worksheet.write_string (row, col+7,x.tax_dedt)
				worksheet.write_string (row, col+8,x.tax_paid)
				worksheet.write_string (row, col+9,x.close_bal)
			row += 1
		workbook.close()



