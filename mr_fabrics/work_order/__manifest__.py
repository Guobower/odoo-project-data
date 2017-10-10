# -*- coding: utf-8 -*-
{
    'name': "work_order",

    'summary': """
        work_order""",

    'description': """
        work_order
    """,

    'author': "ECUBE",
    'website': "http://www.oxenlab.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
    ],
}