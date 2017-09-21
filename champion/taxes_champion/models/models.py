# -*- coding: utf-8 -*-

from odoo import models, fields, api
# import sys
# sys.setrecursionlimit(10000) 
class taxes_champion(models.Model):
    _inherit = 'account.tax'

    type_tax_use        = fields.Selection([
                            ('sale', 'Sales'),
                            ('purchase', 'Purchases'),
                            ('none', 'None'),
                            ('payment', 'Payment'),
                            ('receipt', 'Receipt'),
                            ('salary', 'Salary'),
                            ])
    amount_type         = fields.Selection([
                            ('group', 'Group of Taxes'),
                            ('fixed', 'Fixed'),
                            ('percent', 'Percentage of Price'),
                            ('division', 'Percentage of Price Tax Included')
                            ])
    cp_sales_type       = fields.Many2one('sales.type.bcube','Sales Type')
    cp_sro_no           = fields.Many2one('sro.schno.bcube','SRO No. /Schedule No')
    cp_item_sr_no       = fields.Many2one('item.srno.bcube','Item Sr. No')
    cp_item_desc        = fields.Many2one('item.desc.bcube','Description')
    fbr_tax_code        = fields.Char(string="FBR Tax Code")
    enable_child_tax    = fields.Boolean('Tax on Children')


class SalesTypeBcube(models.Model):
    _name               = 'sales.type.bcube'
    name                = fields.Char('Name')


class ItemSrnoBcube(models.Model):
    _name               = 'item.srno.bcube'
    name                = fields.Char('Name')


class SroSchnoBcube(models.Model):
    _name               = 'sro.schno.bcube'
    name                = fields.Char('Name')


class ItemDescBcube(models.Model):
    _name               = 'item.desc.bcube'
    name                = fields.Char('Name')


class AccountInvoiceBcube(models.Model):
    _inherit            = 'account.invoice'

    @api.one
    def _compute_amount(self):
        res = super(AccountInvoiceBcube, self)._compute_amount()
        self.amount_tax = sum(line.amount for line in self.tax_line_ids)
        self.amount_total = self.amount_untaxed + self.amount_tax
        return res

    @api.onchange('invoice_line_ids')
    def _onchange_invoice_line_ids(self):
        res = super(AccountInvoiceBcube, self)._onchange_invoice_line_ids()
        self.tax_line_ids = 0
        records = []
        taxes_ids = []
        for taxes in self.invoice_line_ids:
            for tax in taxes.bcube_taxes_id:
                if tax.id not in taxes_ids:
                    taxes_ids.append(tax.id)
                    
                    records.append({
                        'name':tax.name,
                        'account_id':tax.account_id.id,
                        'invoice_id':self.id,
                        'tax_id':tax.id,
                        'amount': 0,
                        })
                
            self.tax_line_ids = records
        for taxes in self.invoice_line_ids:
            for tax in taxes.bcube_taxes_id:
                unit_price = taxes.price_unit -(taxes.price_unit * (taxes.discount/100) )
                amount_tax = self.invoice_line_ids.calculateTaxAmount(tax,taxes.quantity,unit_price)
                if self.tax_line_ids:
                    for line in self.tax_line_ids:
                        if line.name == tax.name:
                            line.amount = line.amount + amount_tax
        return res

class AccountInvoiceLineBcube(models.Model):
    _inherit            = 'account.invoice.line'
    bcube_taxes_id      = fields.Many2many('account.tax',
        'account_invoice_line_tax', 'invoice_line_id', 'tax_id',
        string='Taxes', domain=[('type_tax_use','!=','none'), '|', ('active', '=', False), ('active', '=', True)], oldname='invoice_line_tax_id')
    bcube_amount_tax    = fields.Float(string = "Amount Tax")


    @api.onchange('bcube_taxes_id','price_unit','quantity','discount')
    def onChBcubeTaxes(self):
        unit_price = self.price_unit -(self.price_unit * (self.discount/100) )
        self.bcube_amount_tax = self.calculateTaxAmount(self.bcube_taxes_id, self.quantity, unit_price)


    @api.onchange('product_id')
    def getProductTaxes(self):
        all_taxes = []
        for x in self.invoice_id.partner_id.property_account_position_id.tax_ids:
            all_taxes.append((4,x.tax_dest_id.id))

        self.bcube_taxes_id = all_taxes
        self.discount = self.invoice_id.partner_id.discount
        

    def calculateTaxAmount(self, taxes, qty, price_unit):
        amount_tax = 0
        child_tax = 0
        for tax in taxes:
            if tax.enable_child_tax:
                if tax.children_tax_ids:
                    child_tax = 0
                    for childtax in tax.children_tax_ids:
                        child_amount_tax = qty * price_unit * (childtax.amount/100) * (tax.amount/100)
        
                        child_tax = child_tax + child_amount_tax 
                    parent_tax = qty * price_unit * (tax.amount /100)
                    amount_tax = child_tax + parent_tax
            else:
                amount_tax += qty * price_unit * (tax.amount /100)
        
        return amount_tax

class DiscountAmount(models.Model):
    _inherit  = 'res.partner'
    discount = fields.Float(string="Discount%")


# class product_variant_extension(models.Model):
#     _inherit = 'product.product'
  

#     @api.multi
#     def update_names(self):
#         all_products = self.env['product.product'].search([])
#         all_attributes = []
        # for x in all_products:
        #     all_attributes = []
        #     if x.name and x.attribute_value_ids:
        #         # name = x.name
        #         # req_name = name.split()
        #         x.name = str(x.name)+" "+ str(x.attribute_value_ids.name)
        #         # x.name = all_attributes
        #         print "xxxxxxxxxXXXXXX"
        #         print x.id       
        #         print x.name       
        #         print x.attribute_value_ids.name       

        # for x in all_products:
        #     all_attributes = []
        #     if x.name and x.attribute_value_ids:
        #         name = x.name
        #         req_name = name.split()
        #         for y in x.attribute_value_ids:
        #             all_attributes = str(req_name[0])+" "+ str(y.name)
        #             x.name = all_attributes



    # @api.model
    # def create(self, vals): 
    #     new_record = super(product_variant_extension, self).create(vals)
    #     all_attributes = ""
    #     for x in new_record.attribute_value_ids:
    #         all_attributes = str(all_attributes) + str(x.name)
    #     new_record.name = str(new_record.name)+ " " + all_attributes

    #     return new_record

    # @api.onchange('attribute_value_ids','name')
    # def _onchange_attribute_value_ids(self):
    #     all_attributes = []
    #     if self.name and self.attribute_value_ids:
    #         name = self.name
    #         req_name = name.split()
    #         for x in self.attribute_value_ids:
    #             all_attributes = str(req_name[0])+" "+ str(x.name)
    #             self.name = all_attributes       


    # @api.onchange('attribute_value_ids','name')
    # def _onchange_attribute_value_ids(self):
    #     all_attributes = []
    #     name = self.name
    #     req_name = name.split()
    #     for x in self.attribute_value_ids:
    #         all_attributes = str(req_name[0])+" "+ str(x.name)
    #         self.name = all_attributes       
    # @api.multi


    # def write(self, vals):
    #     all_attributes = []
    #     name = self.name
    #     req_name = name.split()
    #     for x in self.attribute_value_ids:
    #         all_attributes = str(req_name[0])+" "+ str(x.name)
    #     self.name = "all_attributes"
    #     result = super(product_variant_extension, self).write(vals)

    #     print "xxxxxxxxxxxxxxxxxxXXXXXXXXXXX"
    #     return result



