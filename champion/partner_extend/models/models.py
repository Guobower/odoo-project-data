# -*- coding: utf-8 -*-

from odoo import models, fields, api

class partner_champion(models.Model):
    _inherit = 'res.partner'

    tax_payment = fields.Many2many('account.tax',string="Tax on Payments")
    buyer_type  = fields.Selection([
        ('Registered','Registered'),
        ('Unregistered','Unregistered')
        ],string="Buyer Type")

   