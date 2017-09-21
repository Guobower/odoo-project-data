# -*- coding: utf-8 -*- 
from odoo import models, fields, api

class invoice_extension(models.Model): 
    _inherit = 'account.invoice'

    invoice_address = fields.Char(string="Invoice Address")
    
    delivery_date = fields.Date(string="Delivery Date")
    confirmation_date = fields.Date(string="Confirmation Date")
    invoice_bank = fields.Many2one('res.bank',string="Bank")
    
    ship_via = fields.Selection([
        ('bysea', 'By Sea'),
        ('byair', 'By Air'),
        ('byland', 'By Land'),
        ],default='bysea', string="Ship via")