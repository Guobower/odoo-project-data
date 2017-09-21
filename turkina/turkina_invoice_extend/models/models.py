# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from odoo import models, fields, api
 

class taxes_champion(models.Model):
    _inherit = 'account.invoice'

    due_date      = fields.Date(string="Due Date")
    give_discount = fields.Boolean(string="Give Discount")
    days          = fields.Integer(string="Days")
    percent       = fields.Float(string="Percent")



    @api.onchange('date_invoice')
    def due_Date(self):
    	if self.payment_term_id and self.date_invoice:
    		start_date = datetime.strptime(self.date_invoice,"%Y-%m-%d")
    		if self.payment_term_id.name == "15 Days":
    			self.due_date = start_date + timedelta(days=15)
    		elif self.payment_term_id.name == "30 Days":
    			self.due_date = start_date + timedelta(days=30)
    		elif self.payment_term_id.name == "60 Net Days":
    			self.due_date = start_date + timedelta(days=60)
    		elif self.payment_term_id.name == "90 Days":
    			self.due_date = start_date + timedelta(days=90)
    		else:
    			self.due_date = self.date_invoice



class turkina_extend(models.Model):
    _inherit = 'sale.order'

    give_discount = fields.Boolean(string="Give Discount")
    days          = fields.Integer(string="Days")
    percent       = fields.Float(string="Percent")






