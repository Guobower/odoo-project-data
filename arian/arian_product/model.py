# -*- coding: utf-8 -*- 
from odoo import models, fields, api

class product_extension(models.Model): 
    _inherit = 'product.template'

    article_num = fields.Char(string="Article Number")
    customer_ref = fields.Char(string="Customer Reference No")
    bill_ref = fields.Char(string="Bill of Material Reference #")
    internal_ref = fields.Char(string="Item Code")
    inner_carton = fields.Char(string="Inner Carton")
    pcs_carton = fields.Char(string="Pcs/Carton")
    style_no = fields.Char(string="Style No.")

    prod_customer = fields.Many2one('res.partner',string="Customer", domain=[('customer','=',True)] )

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
    carton_master_height = fields.Float(string="Height")

    material_descrip = fields.Text(string="Material for Description")
    workmanship_descrip = fields.Text(string="Description for Workmanship")
    decor_descrip = fields.Text(string="Description for Decor")
    packing_descrip = fields.Text(string="Description for Packing")

    @api.onchange('prod_customer')
    def onchange_customer(self):
        if self.prod_customer:
            # self.length = self.prod_customer.length
            self.width = self.prod_customer.width
            self.height = self.prod_customer.height
            self.weight = self.prod_customer.weight
            self.size_from = self.prod_customer.size_from
            self.size_to = self.prod_customer.size_to
            # self.carton_lenght = self.prod_customer.carton_lenght
            self.carton_width = self.prod_customer.carton_width
            self.carton_height = self.prod_customer.carton_height
            self.carton_weight = self.prod_customer.carton_weight
            self.inner_carton = self.prod_customer.inner_carton
            self.pcs_carton = self.prod_customer.pcs_carton
            self.carton_master_height = self.prod_customer.master_height

    @api.multi
    def write(self, vals):
        result = super(product_extension, self).write(vals)

        for x in self.product_variant_ids:

            x.internal_ref = self.internal_ref
            x.article_num = self.article_num
            x.customer_ref = self.customer_ref
            x.bill_ref = self.bill_ref
            x.prod_customer = self.prod_customer
            x.style_no = self.style_no
        return result

class product_extension_varient(models.Model): 
    _inherit = 'product.product'

    article_num = fields.Char(string="Article Number")
    customer_ref = fields.Char(string="Customer Reference No")
    bill_ref = fields.Char(string="Bill of Material Reference #")
    internal_ref = fields.Char(string="Item Code")
    style_no = fields.Char(string="Style No.")

    prod_customer = fields.Many2one('res.partner',string="Customer", domain=[('customer','=',True)] )
    
    # @api.model
    # def create(self, vals):
    #     new_record = super(product_extension_varient, self).create(vals)
    #     new_record.internal_ref = new_record.product_tmpl_id.internal_ref
    #     new_record.article_num = new_record.product_tmpl_id.article_num
    #     new_record.customer_ref = new_record.product_tmpl_id.customer_ref
    #     new_record.bill_ref = new_record.product_tmpl_id.bill_ref
    #     new_record.prod_customer = new_record.product_tmpl_id.prod_customer
    #     new_record.style_no = new_record.product_tmpl_id.style_no
    #     return

class product_quality_note(models.Model): 
    _name = 'quality.note'
    _rec_name= 'prod_customer'

    prod_customer = fields.Many2one('res.partner',string="Customer", domain=[('customer','=',True)] )
    product = fields.Many2one('product.product',string="Products" )

    style = fields.Char(string="Style")
    m_order = fields.Char(string="MO #")
    date = fields.Date(string="date")