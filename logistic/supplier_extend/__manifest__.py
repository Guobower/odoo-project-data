# -*- coding: utf-8 -*-
{
    'name': "supplier_extend",

    'summary': """
        supplier_extend""",

    'description': """
        supplier_extend
    """,

    'author': "ECUBE",
    'website': "http://www.oxenlab.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','account','sale','quote_extend'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
    ],
}