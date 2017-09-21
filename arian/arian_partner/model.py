# -*- coding: utf-8 -*- 
from odoo import models, fields, api

class partner_extension(models.Model): 
    _inherit = 'res.partner' 

    forwarder = fields.Boolean()

    forwarder_name = fields.Many2one('res.partner',string="Forwarder Name", domain=[('forwarder','=',True)] )
    incoterms = fields.Many2one('stock.incoterms',string="Incoterms" )

    # length = fields.Float(string="Lenght")
    width = fields.Float(string="Width")
    height = fields.Float(string="Height")
    weight = fields.Float(string="Weight (Gms)")
    size_from = fields.Float(string="Size From")
    size_to = fields.Float(string="Size to")
    # carton_lenght = fields.Float(string="Lenght")
    carton_width = fields.Float(string="Width")
    carton_height = fields.Float(string="Height")
    carton_weight = fields.Float(string="Weight (Gms)")
    master_height = fields.Float(string="Height")

    inner_carton = fields.Char(string="Inner Carton")
    pcs_carton = fields.Char(string="Pcs/Carton")

class saleorder_extension(models.Model): 
    _inherit = 'sale.order' 

    @api.onchange('partner_id')
    def onchange_incoterm(self):
        if self.partner_id:
    	   self.incoterm = self.partner_id.incoterms.id

class stockincoterms_extension(models.Model): 
    _inherit = 'stock.incoterms'

    _rec_name = 'code' 