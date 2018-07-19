# -*- coding: utf-8 -*-
{
    'name': "Trips and Compensations",
    'application': True,

    'summary': """
        Trips and compensations planning
    """,

    'description': """
        This module adds trip planning and compensation calculations for managing a transportation company.
    """,

    'author': "janbkrejci@gmail.com",
    'website': "http://www.podnikovy-system.cz",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Business Applications',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'hr', 'fleet'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
