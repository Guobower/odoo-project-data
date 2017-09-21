# -*- coding: utf-8 -*-
{
    'name': "Ixon Performa Invoice",

    'summary': "Ixon Performa Invoice",

    'description': "Ixon Performa Invoice",

    'author': "Muhammmad Kamran",
    'website': "http://www.bcube.com",

    # any module necessary for this one to work correctly
    'depends': ['base', 'report','account'],
    # always loaded
    'data': [
        'template.xml',
        'views/module_report.xml',
    ],
    'css': ['static/src/css/report.css'],
}
