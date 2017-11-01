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

from odoo import models, fields, api
from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT
from openerp.exceptions import Warning

class SampleDevelopmentReport(models.AbstractModel):
    _name = 'report.product_ledger.product_ledger_report'

    @api.model
    def render_html(self,docids, data=None):

        report_obj = self.env['report']
        report = report_obj._get_report_from_name('product_ledger.product_ledger_report')
        active_wizard = self.env['product.ledger'].search([])

        emp_list = []
        for x in active_wizard:
            emp_list.append(x.id)
        emp_list = emp_list
        emp_list_max = max(emp_list) 

        record_wizard = self.env['product.ledger'].search([('id','=',emp_list_max)])
        record_wizard_del = self.env['product.ledger'].search([('id','!=',emp_list_max)])
        record_wizard_del.unlink()

        to = record_wizard.to
        form = record_wizard.form
        product = record_wizard.product

        date = datetime.now().date()
        timed = datetime.now().time().strftime("%H:%M")

        records = self.env['product.product'].search([('id','=',product.id)])

        invoices = self.env['account.invoice'].search([('date_invoice','>=',form),('date_invoice','<=',to)])

        last_purchase = self.env['account.invoice'].search([('type','=','in_invoice'),('date_invoice','<',form)])

        last_purchased = []
        dates = []
        for x in last_purchase:
            for y in x.invoice_line_ids:
                if y.product_id == product:
                    last_purchased.append(x)
                    dates.append(x.date_invoice)

        dates.sort()

        for x in dates:
            last = x

        def last_quantity(attr):
            for x in last_purchased:
                if x.date_invoice == last:
                    for y in x.invoice_line_ids:
                        if y.product_id == product:
                            if attr == 'qty':
                                return y.quantity
                            if attr == 'date':
                                return x.date_invoice
                            if attr == 'unit':
                                return y.product_id.uom

        required_invoices = []
        for x in invoices:
            for y in x.invoice_line_ids:
                if y.product_id == product:
                    required_invoices.append(x)

        def line_data(data,attr):
            for x in required_invoices:
                if x == data:
                    for y in x.invoice_line_ids:
                        if y.product_id == product:
                            if attr == 'unit_price':
                                return y.price_unit
                            if attr == 'qty':
                                return y.quantity
            
        docargs = {
            'doc_ids': docids,
            'doc_model': 'product.product',
            'docs': records,
            'data': data,
            'to': to,
            'form': form,
            'date': date,
            'timed': timed,
            'required_invoices': required_invoices,
            'line_data': line_data,
            'last_quantity': last_quantity
        }

        return report_obj.render('product_ledger.product_ledger_report', docargs)