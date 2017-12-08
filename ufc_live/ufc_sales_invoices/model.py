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
###################################################
from openerp import models, fields, api
from num2words import num2words

class SampleDevelopmentReport(models.AbstractModel):
    _name = 'report.ufc_sales_invoices.module_report'

    @api.model
    def render_html(self,docids, data=None):
        report_obj = self.env['report']
        report = report_obj._get_report_from_name('ufc_sales_invoices.module_report')
        records = self.env['account.invoice'].browse(docids)


        def shift():
            prov = ""
            for x in records:
                if x.province:
                    prov = x.province
            
            return prov

        def name():
            name = ""
            for x in records:
                if x.partner_id:
                    name = x.partner_id.name
            
            return name

        def bill():
            new = 0
            rec = self.env['summary.ffc'].search([('pun_invoice.id','=',records.id)])
            if rec.Customer.name == "FFC Goth Machi":
                new = rec.pun_num
            if rec.Customer.name == "FFC Mir Pur Mathelo":
                new = rec.inv_no

            return new 


        def sinbill():
            new = 0
            rec = self.env['summary.ffc'].search([('sin_invoice.id','=',records.id)])
            if rec.Customer.name == "FFC Goth Machi":
                new = rec.sin_num
            if rec.Customer.name == "FFC Mir Pur Mathelo":
                new = rec.inv_no1

            return new 

        def number_to_spell(attrb):
            word = num2words((attrb))
            word = word.title() + " " + "Only"
            return word


                           

        docargs = {
            'doc_ids': docids,
            'doc_model': 'account.invoice',
            'docs': records,
            'data': data,
            'shift': shift,
            'bill': bill,
            'name': name,
            'sinbill': sinbill,
            'number_to_spell': number_to_spell
            }

        return report_obj.render('ufc_sales_invoices.module_report', docargs)


