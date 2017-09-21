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
    _name = 'report.ixon_performa_invoice.module_report'

    @api.model
    def render_html(self,docids, data=None):
        report_obj = self.env['report']
        report = report_obj._get_report_from_name('ixon_performa_invoice.module_report')
        records = self.env['account.invoice'].browse(docids)

        enteries = []
        for x in records.invoice_line_ids:
          if x.product_id.product_tmpl_id not in enteries:
               enteries.append(x.product_id.product_tmpl_id)

        varients = []
        def getdata(current_record,attrb):
            del varients[:]
            for x in records.invoice_line_ids:
                if x.product_id.product_tmpl_id == current_record:
                    varients.append(x)

            if attrb == "style":
                style = ""
                for x in records.invoice_line_ids:
                    if x.product_id.product_tmpl_id == current_record:
                        style = x.product_id.style_no
                return style

            if attrb == "desc":
                desc = ""
                for x in records.invoice_line_ids:
                    if x.product_id.product_tmpl_id == current_record:
                        desc = x.name
                return desc


            # if attrb == "rate":
            #     rate = ""
            #     for x in records.invoice_line_ids:
            #         if x.product_id.product_tmpl_id == current_record:
            #             rate = x.price_unit
            #     return rate

            
            # if attrb == "amount":
            #     amount = 0
            #     for x in varients:
            #         print x.price_subtotal
            #         amount = amount + x.price_subtotal
            #     return amount


            if attrb == "xs_size":
                xs_size = 0
                for x in varients:
                    for y in x.product_id.attribute_value_ids:
                        if y.name == "xs":
                            xs_size = xs_size + x.quantity
                return xs_size

            if attrb == "s_size":
                s_size = 0
                for x in varients:
                    for y in x.product_id.attribute_value_ids:
                        if y.name == "s":
                            s_size = s_size + x.quantity
                return s_size

            if attrb == "m_size":
                m_size = 0
                for x in varients:
                    for y in x.product_id.attribute_value_ids:
                        if y.name == "m":
                            m_size = m_size + x.quantity
                return m_size 

            if attrb == "l_size":
                l_size = 0
                for x in varients:
                    for y in x.product_id.attribute_value_ids:
                        if y.name == "l":
                            l_size = l_size + x.quantity
                return l_size


            if attrb == "xl_size":
                xl_size = 0
                for x in varients:
                    for y in x.product_id.attribute_value_ids:
                        if y.name == "xl":
                            xl_size = xl_size + x.quantity
                return xl_size

            if attrb == "xxl_size":
                xxl_size = 0
                for x in varients:
                    for y in x.product_id.attribute_value_ids:
                        if y.name == "xxl":
                            xxl_size = xxl_size + x.quantity
                return xxl_size

            if attrb == "3xl_size":
                _3xl_size = 0
                for x in varients:
                    for y in x.product_id.attribute_value_ids:
                        if y.name == "3xl":
                            _3xl_size = _3xl_size + x.quantity
                return _3xl_size

            if attrb == "4xl_size":
                _4xl_size = 0
                for x in varients:
                    for y in x.product_id.attribute_value_ids:
                        if y.name == "4xl":
                            _4xl_size = _4xl_size + x.quantity
                return _4xl_size


            if attrb == "5xl_size":
                _5xl_size = 0
                for x in varients:
                    for y in x.product_id.attribute_value_ids:
                        if y.name == "5xl":
                            _5xl_size = _5xl_size + x.quantity
                return _5xl_size



            if attrb == "xs_rate":
                xs_rate = 0
                for x in varients:
                    for y in x.product_id.attribute_value_ids:
                        if y.name == "xs":
                            xs_rate = xs_rate + x.price_unit
                return xs_rate

            if attrb == "s_rate":
                s_rate = 0
                for x in varients:
                    for y in x.product_id.attribute_value_ids:
                        if y.name == "s":
                            s_rate = s_rate + x.price_unit
                return s_rate

            if attrb == "m_rate":
                m_rate = 0
                for x in varients:
                    for y in x.product_id.attribute_value_ids:
                        if y.name == "m":
                            m_rate = m_rate + x.price_unit
                return m_rate 

            if attrb == "l_rate":
                l_rate = 0
                for x in varients:
                    for y in x.product_id.attribute_value_ids:
                        if y.name == "l":
                            l_rate = l_rate + x.price_unit
                return l_rate


            if attrb == "xl_rate":
                xxl_rate = 0
                for x in varients:
                    for y in x.product_id.attribute_value_ids:
                        if y.name == "xl":
                            xxl_rate = xxl_rate + x.price_unit
                return xxl_rate

            if attrb == "xxl_rate":
                xxl_rate = 0
                for x in varients:
                    for y in x.product_id.attribute_value_ids:
                        if y.name == "xxl":
                            xxl_rate = xxl_rate + x.price_unit
                return xxl_rate

            if attrb == "3xl_rate":
                _3xl_rate = 0
                for x in varients:
                    for y in x.product_id.attribute_value_ids:
                        if y.name == "3xl":
                            _3xl_rate = _3xl_rate + x.price_unit
                return _3xl_rate

            if attrb == "4xl_rate":
                _4xl_rate = 0
                for x in varients:
                    for y in x.product_id.attribute_value_ids:
                        if y.name == "4xl":
                            _4xl_rate = _4xl_rate + x.price_unit
                return _4xl_rate


            if attrb == "5xl_rate":
                _5xl_rate = 0
                for x in varients:
                    for y in x.product_id.attribute_value_ids:
                        if y.name == "5xl":
                            _5xl_rate = _5xl_rate + x.price_unit
                return _5xl_rate


            if attrb == "xs_amount":
                xs_amount = 0
                for x in varients:
                    for y in x.product_id.attribute_value_ids:
                        if y.name == "xs":
                            xs_amount = xs_amount + x.price_subtotal
                return xs_amount


            if attrb == "s_amount":
                s_amount = 0
                for x in varients:
                    for y in x.product_id.attribute_value_ids:
                        if y.name == "s":
                            s_amount = s_amount + x.price_subtotal
                return s_amount


            if attrb == "m_amount":
                m_amount = 0
                for x in varients:
                    for y in x.product_id.attribute_value_ids:
                        if y.name == "m":
                            m_amount = m_amount + x.price_subtotal
                return m_amount


            if attrb == "l_amount":
                l_amount = 0
                for x in varients:
                    for y in x.product_id.attribute_value_ids:
                        if y.name == "l":
                            l_amount = l_amount + x.price_subtotal
                return l_amount

            if attrb == "xl_amount":
                xl_amount = 0
                for x in varients:
                    for y in x.product_id.attribute_value_ids:
                        if y.name == "xl":
                            xl_amount = xl_amount + x.price_subtotal
                return xl_amount

            if attrb == "xxl_amount":
                xxl_amount = 0
                for x in varients:
                    for y in x.product_id.attribute_value_ids:
                        if y.name == "xxl":
                            xxl_amount = xxl_amount + x.price_subtotal
                return xxl_amount


            if attrb == "3xl_amount":
                _3xl_amount = 0
                for x in varients:
                    for y in x.product_id.attribute_value_ids:
                        if y.name == "3xl":
                            _3xl_amount = _3xl_amount + x.price_subtotal
                return _3xl_amount

            if attrb == "4xl_amount":
                _4xl_amount = 0
                for x in varients:
                    for y in x.product_id.attribute_value_ids:
                        if y.name == "4xl":
                            _4xl_amount = _4xl_amount + x.price_subtotal
                return _4xl_amount


            if attrb == "5xl_amount":
                _5xl_amount = 0
                for x in varients:
                    for y in x.product_id.attribute_value_ids:
                        if y.name == "5xl":
                            _5xl_amount = _5xl_amount + x.price_subtotal
                return _5xl_amount


            if attrb == "color":
                color = ''
                colors = []
                for x in varients:
                    for y in x.product_id.attribute_value_ids:
                        if y.attribute_id.name == "colour":
                            if color == '':
                                colors.append(y.name)
                                color = y.name
                            else:
                                if y.name not in color:
                                    colors.append(y.name)
                                    color = color + " , " + y.name
                return color



            


        docargs = {
        'doc_ids': docids,
        'doc_model': 'account.invoice',
        'docs': records,
        'data': data,
        'entries': enteries,
        'getdata': getdata
        }

        return report_obj.render('ixon_performa_invoice.module_report', docargs)

                ##################### pip install num2words ################################


class Num2Words(models.Model):
    _inherit = 'account.invoice'

    @api.multi
    def number_to_words(self):
        word = num2words((self.amount_untaxed))
        word = word.title() + " " + "Only"
        return word