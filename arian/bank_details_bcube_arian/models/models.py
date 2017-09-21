# -*- coding: utf-8 -*-

from odoo import models, fields, api

class bank_details_bcube(models.Model):
    _inherit = 'res.partner.bank'

    iban_acc_no  = fields.Char(string="IBAN Account Number")
    swift_code = fields.Char(string="Swift Code")
    branch = fields.Char(string="Branch")
    branch_code = fields.Char(string="Branch Code")
    bank_address = fields.Text(string="Bank Address")

class bank_only_details_bcube(models.Model):
    _inherit = 'res.bank'

    iban_acc_no  = fields.Char(string="IBAN Account Number")
    swift_code = fields.Char(string="Swift Code")
    branch = fields.Char(string="Branch")
    branch_code = fields.Char(string="Branch Code")
    account_number = fields.Char(string="Account Number")
