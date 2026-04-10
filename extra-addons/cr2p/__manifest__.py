# -*- coding: utf-8 -*-
{
    'name': "CR2P",
    'sequence': 1,
    'summary': """
        """,

    'description': """
        
    """,

    'author': "Fabien BIBE",
    'website': "https://www.websystem.fr",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '19.0.0.9',

    # any module necessary for this one to work correctly
    'depends': ['base', 'contacts', 'sale', 'stock', 'sale_management', 'account_accountant', 'calendar', 'sign', 'sale_pdf_quote_builder', 'mail'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'security/ir_rules.xml',

        'data/account_data.xml',
        'data/commune.csv',
        'data/fonction.csv',
        'data/forme_juridique.csv',
        'data/source_contacts.csv',
        'data/ir_sequence_data.xml',
        'data/channel_approbation_remise.xml',

        'views/calendar_views.xml',
        'views/sale_order_views.xml',
        'views/source_contacts_views.xml',
        'views/forme_juridique_views.xml',
        'views/fonction_views.xml',
        'views/commune_views.xml',
        'views/utilisateur_views.xml',
        'views/contact_views.xml',
        'views/sale_portal_template.xml',
        'views/only_own_contacts.xml',

        'wizard/sale_order_cerfa_view.xml',

        'report/sale_order_document.xml',
        'report/sale_report_views.xml',
        'report/ir_actions_report_templates.xml',
    ],
    "assets": {
        "web.assets_backend": [
            'cr2p/static/src/**/*',
        ],
    },
    # only loaded in demonstration mode
    'demo': [
        'data/cerfa_cgv_pdf.xml',
    ],
    'installable': True,
    'auto_install': True,
}
