# -*- coding: utf-8 -*-

import os
import xlsxwriter
from odoo import models, fields, api

class wizard(models.Model):
    _name = 'arian.invoice.report'

    @api.multi
    def compute_sheet(self):
        result = self.env['account.invoice'].browse(self._context.get('active_ids'))
        for line in result:
            print "This is working...!"
            line_number = line.number
            line_number = line_number.split("/")
            line_number = line_number[0]+"-"+line_number[1]+"-"+line_number[2]+".xlsx"
            path = os.path.join(os.path.expanduser('~'), 'Documents', line_number)
            workbook = xlsxwriter.Workbook(line_number)
            worksheet = workbook.add_worksheet()
            # Add a bold format to use to highlight cells.
            headline_format = workbook.add_format({
                'bold': 20,
                'border': 2,
                'align': 'center',
                'valign': 'bottom'})
            headline_format.set_font_size(20)

            performa_format = workbook.add_format({
                'bold': 1,
                'border': 2,
                'align': 'center',
                'valign': 'vcenter'})
            performa_format.set_font_size(20)

            invoice_format = workbook.add_format({
                'bg_color': '#999999',
                'pattern': 1,
                'border': 2,
                })

            bold = workbook.add_format({
                'bold': 1,
                'bg_color': '#999999',
                'align': 'center',
                'valign': 'vcenter'
                })

            ship_to = workbook.add_format({
                'bold': 1,
                'align': 'center',
                'valign': 'vcenter'
                })
            worksheet.merge_range('J9:K9', 'Invoice No.', invoice_format)
            worksheet.merge_range('J10:K10', 'Invoice Date', invoice_format)
            worksheet.merge_range('J11:K11', 'BL NUMBER', invoice_format)
            worksheet.merge_range('J12:K12', 'BL DATE', invoice_format)
            worksheet.merge_range('J13:K13', 'FOAM E NO', invoice_format)
            worksheet.merge_range('J14:K14', 'FOAM E NO', invoice_format)

            worksheet.merge_range('L9:N9', line.number, invoice_format)
            worksheet.merge_range('L10:N10', 'Invoice Date', invoice_format)
            worksheet.merge_range('L11:N11', 'BL NUMBER', invoice_format)
            worksheet.merge_range('L12:N12', 'BL DATE', invoice_format)
            worksheet.merge_range('L13:N13', 'FOAM E NO', invoice_format)
            worksheet.merge_range('L14:N14', 'FOAM E NO', invoice_format)

            filename   = 'arian.jpg'
            worksheet.insert_image('A1', filename, {'x_scale': 2.27, 'y_scale': 1.43})


            worksheet.merge_range('A1:N6', '              Arian Sports (Pvt) Ltd \n               1Km off Naul More Roras Road Sialkot Pakistan',headline_format)
            worksheet.merge_range('A7:N8', 'PROFORMA INVOICE ',performa_format)

            worksheet.write('A9', 'Ship To:',ship_to)
            worksheet.write_string  (9, 1,'ATTEN:'+line.partner_id.name)
            worksheet.write_string  (10, 1,line.partner_id.street)
            worksheet.write_string  (11, 1,line.partner_id.city)
            worksheet.write_string  (12, 1, str(line.partner_id.zip))
            worksheet.write_string  (13, 1,line.partner_id.country_id.name)
            worksheet.write_string  (14, 1,'TEL: '+line.partner_id.phone)
            worksheet.write_string  (15, 1,line.partner_id.email)

            worksheet.set_row(16, 30)
            worksheet.set_column('A:N', 11)

            worksheet.write('A17', 'Pos.',bold)
            worksheet.write('B17', 'External \n Art-Code',bold)
            worksheet.write('C17', 'IXS Art \n Code',bold)
            worksheet.write('D17', 'IXS Colour \n Code',bold)
            worksheet.write('E17', 'IXS \n SIZE',bold)
            worksheet.write('F17', 'Product Name',bold)
            worksheet.write('G17', 'colour',bold)
            worksheet.write('H17', 'Order \n Qty',bold)
            worksheet.write('I17', 'Unit',bold)
            worksheet.write('J17', 'Unit \n Price',bold)
            worksheet.write('K17', 'Order \n Value',bold)
            worksheet.write('L17', 'Currency',bold)
            worksheet.write('M17', 'IXS PO-\nno',bold)
            worksheet.write('N17', 'Ex-factory \n Date',bold)

            row = 17
            col = 0
            for item  in line.invoice_line_ids:
                worksheet.write_string  (row, col,item.product_id.name)
                worksheet.write_string  (row, col+1,item.product_id.name)
                worksheet.write_string  (row, col+2,item.product_id.name)
                worksheet.write_string  (row, col+3,item.product_id.name)
                worksheet.write_string  (row, col+4,item.product_id.name)
                worksheet.write_string  (row, col+5,item.product_id.name)
                worksheet.write_string  (row, col+6,item.product_id.name)
                worksheet.write_string  (row, col+7,item.product_id.name)
                worksheet.write_string  (row, col+8,item.product_id.name)
                worksheet.write_string  (row, col+9,item.product_id.name)
                worksheet.write_string  (row, col+10,item.product_id.name)
                worksheet.write_string  (row, col+11,item.product_id.name)
                worksheet.write_string  (row, col+12,item.product_id.name)
                worksheet.write_string  (row, col+13,item.product_id.name)

                row += 1
            worksheet.merge_range(row , 0, row, 3, 'TOTAL VALUE', invoice_format)
            worksheet.merge_range(row , 4, row, 6, '', invoice_format)
            worksheet.write_string  (row, col+7,item.product_id.name, invoice_format)
            worksheet.merge_range(row , 8, row, 9, '', invoice_format)
            worksheet.write_string  (row, col+10,item.product_id.name, invoice_format)
            worksheet.merge_range(row , 11, row, 13, '', invoice_format)

            worksheet.merge_range(row+1 , 0, row+1, 3, 'Less 2% warranty Discount')
            worksheet.write_string  (row+1, col+10,item.product_id.name)

            worksheet.merge_range(row+2 , 0, row+2, 7, 'Sub - Total', invoice_format)
            worksheet.merge_range(row+2 , 8, row+2, 13, 'Us$ '+item.product_id.name, invoice_format)


            worksheet.merge_range(row+3 , 0, row+3, 1, 'Term Of Payment:', ship_to)
            worksheet.write_string  (row+3, 2 ,'100% TT after inspection & Before Shipment ')


            worksheet.merge_range(row+5 , 0, row+5, 1, 'Term of Delivery :', ship_to)
            worksheet.write_string  (row+5, 2 ,item.product_id.name)
            worksheet.write_string  (row+5, 3 ,'Ship From:', ship_to)
            worksheet.write_string  (row+5, 4 ,item.product_id.name)
            worksheet.write_string  (row+5, 5 ,'Ship From:', ship_to)
            worksheet.write_string  (row+5, 6 ,item.product_id.name)

            worksheet.merge_range(row+7 , 0, row+7, 1, 'Bank- Detail:',ship_to)
            worksheet.write_string  (row+7, 2 ,item.product_id.name)
            worksheet.write_string  (row+8, 2 ,item.product_id.name)
            worksheet.write_string  (row+9, 2 ,item.product_id.name)
            worksheet.write_string  (row+10, 2 ,item.product_id.name)
            worksheet.write_string  (row+11, 2 ,item.product_id.name)
            worksheet.write_string  (row+12, 2 ,item.product_id.name)
            worksheet.write_string  (row+13, 2 ,item.product_id.name)
            worksheet.write_string  (row+14, 2 ,item.product_id.name)

            worksheet.set_row(row+15, 30)
            worksheet.merge_range(row+15 , 0, row+15, 13, 'BUILDING NUMBER 11/224 NEKA PURA, PULL AIK SIALKOT - PAKISTAN \n TEL: 0092-321-5377135 , FAX: 0092-52-613005 , ecostar1982@gmail.com - web www.ecostar1982.com',bold)

            workbook.close()