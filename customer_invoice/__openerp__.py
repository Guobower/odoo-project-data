# -*- coding: utf-8 -*-
{
    'name': "Tagm Customer Invoice",

    'summary': "Tagm Customer Invoice",

    'description': "Tagm Customer Invoice",

    'author': "Muhammad Kamran",
    'website': "http://www.bcube.com",

    # any module necessary for this one to work correctly
    'depends': ['base','account','report'],
    # always loaded
    'data': [
        'template.xml',
        'views/customer_invoice.xml',
    ],
    'css': ['static/src/css/report.css'],
}
