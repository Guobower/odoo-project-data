# -*- coding: utf-8 -*-
from odoo import http

# class ArianInvoiceReport(http.Controller):
#     @http.route('/arian_invoice_report/arian_invoice_report/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/arian_invoice_report/arian_invoice_report/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('arian_invoice_report.listing', {
#             'root': '/arian_invoice_report/arian_invoice_report',
#             'objects': http.request.env['arian_invoice_report.arian_invoice_report'].search([]),
#         })

#     @http.route('/arian_invoice_report/arian_invoice_report/objects/<model("arian_invoice_report.arian_invoice_report"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('arian_invoice_report.object', {
#             'object': obj
#         })