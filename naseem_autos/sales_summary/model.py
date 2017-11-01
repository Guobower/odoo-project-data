#-*- coding:utf-8 -*-
########################################################################################
########################################################################################
##                                                                                    ##
##    OpenERP, Open Source Management Solution                                        ##
##    Copyright (C) 2011 OpenERP SA (<http://openerp.com>). All Rights Reserved       ##
##                                                                                    ##
##    This program is free software: you can redistribute it and/or modify            ##
##    it under the terms of the GNU Affero General Public License as published by     ##
##    the Free Software Foundation, either version 3 of the License, or               ##
##    (at your option) any later version.                                             ##
##                                                                                    ##
##    This program is distributed in the hope that it will be useful,                 ##
##    but WITHOUT ANY WARRANTY; without even the implied warranty of                  ##
##    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the                   ##
##    GNU Affero General Public License for more details.                             ##
##                                                                                    ##
##    You should have received a copy of the GNU Affero General Public License        ##
##    along with this program.  If not, see <http://www.gnu.org/licenses/>.           ##
##                                                                                    ##
########################################################################################
########################################################################################

import time
from odoo import models, fields, api
from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT

class SampleDevelopmentReport(models.AbstractModel):
    _name = 'report.sales_summary.sales_summary_report'

    @api.model
    def render_html(self,docids, data=None):

        report_obj = self.env['report']
        report = report_obj._get_report_from_name('sales_summary.sales_summary_report')
        active_wizard = self.env['sales.summary'].search([])

        emp_list = []
        for x in active_wizard:
            emp_list.append(x.id)
        emp_list = emp_list
        emp_list_max = max(emp_list) 

        record_wizard = self.env['sales.summary'].search([('id','=',emp_list_max)])
        record_wizard_del = self.env['sales.summary'].search([('id','!=',emp_list_max)])
        record_wizard_del.unlink()

        to = record_wizard.to
        form = record_wizard.form

        date = datetime.now().date()
        timed = datetime.now().time().strftime("%H:%M")

        records = self.env['account.invoice'].search([])

        def cashsale():
            direct_invoices = self.env['sale.order'].search([('direct_invoice_check','=','1'),('date_order','>=',form),('date_order','<=',to)])

            direct_payments = 0
            for x in direct_invoices:
                direct_payments = direct_payments + x.amount_total

            return direct_payments

        def creditsale():
            credit_invoices = self.env['account.invoice'].search([('date_invoice','>=',form),('date_invoice','<=',to)])

            credit_payments = 0
            for x in credit_invoices:
                credit_payments = credit_payments + x.amount_total

            return credit_payments

        def cashpay():
            cash_payments = self.env['customer.payment.bcube'].search([('date','>=',form),('date','<=',to),('journal_id.name','=','cash')])

            cash_payment = 0
            for x in cash_payments:
                cash_payment = cash_payment + x.total

            return cash_payment

        def bankpay():
            bank_payments = self.env['customer.payment.bcube'].search([('date','>=',form),('date','<=',to),('journal_id.name','=','Bank')])

            bank_payment = 0
            for x in bank_payments:
                bank_payment = bank_payment + x.total

            return bank_payment


        docargs = {
            'doc_ids': docids,
            'doc_model': 'account.invoice',
            'docs': records,
            'data': data,
            'to':to,
            'form':form,
            'date':date,
            'timed':timed,
            'cashsale': cashsale,
            'creditsale': creditsale,
            'cashpay': cashpay,
            'bankpay': bankpay
        }

        return report_obj.render('sales_summary.sales_summary_report', docargs)