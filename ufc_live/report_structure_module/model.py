# -*- coding: utf-8 -*- 
from odoo import models, fields, api

class ecube_report_structure(models.Model):
    _name = 'ecube.report.structure'
    _rec_name = 'description'

    description = fields.Selection([
        ('balance_sheet', 'Balance Sheet'),
        ('profit_loss', 'Profit and Loss'),
        ('cash', 'Cash Flow'),
        ], string='Description')
    report_link = fields.One2many('ecube.report.structure.details','report_tree')

class ecube_report_structure_details(models.Model):
    _name = 'ecube.report.structure.details'

    description = fields.Many2one('description.class',string="Description")
    account_head = fields.Many2many('account.account',string="Account Head")
    summary = fields.Many2many('description.class',string="Summary Heads")
    level = fields.Integer(string="Level")
    entry_type = fields.Selection([
                        ('heading', 'Heading'),
                        ('account', 'Account'),
                        ('total', 'Total'),
                        ('grand_total', 'Grand Total')
                        ], string='Type')
    nature = fields.Selection([
                        ('debit', 'Debit'),
                        ('credit', 'Credit'),
                        ], string='Nature', default='debit')
    report_tree = fields.Many2one('ecube.report.structure')


class descriptionClass(models.Model):
    _name = 'description.class'

    name    = fields.Char(string="Description")