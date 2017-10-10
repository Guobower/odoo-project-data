# -*- coding: utf-8 -*-

from odoo import models, fields, api


class WorkOrder(models.Model):
	_name = 'work.order'

	buyer = fields.Many2one('res.partner',string="Buyer",required=True)
	merchant  = fields.Char(string="Merchant")
	style     = fields.Char(string="Style")
	