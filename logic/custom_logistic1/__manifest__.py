# -*- coding: utf-8 -*-
{
    'name': "Import/Export Logistic",

    'summary': """
        Nayyab""",

    'description': """
        Long description of module's purpose
    """,

    'author': "My Company",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','sale','account','sale_stock'],

    # always loaded
    'data': [
        'views.xml',
        'quote.xml',
        'supplier.xml',
    ],
    'installable': True,
    'auto_install': False

}