# -*- coding: utf-8 -*-
{
    'name': "Real Estate",

    'summary': "Short (1 phrase/line) summary of the module's purpose",

    'description': """
Long description of module's purpose
    """,

    'author': "My Company",
    'website': "https://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',
    'license': 'LGPL-3',
    # any module necessary for this one to work correctly
    'depends': ['base','account'],

    # always loaded
    'data': [
        "security/ir.model.access.csv",
        "views/project_views.xml",
        "views/building_views.xml",
        "views/property_views.xml",
        "views/pricebook_views.xml",
        "views/property_status_views.xml",
        "views/order_views.xml",
        "views/real_estate_menus.xml"
    ],

}