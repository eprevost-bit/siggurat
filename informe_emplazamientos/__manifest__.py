# -*- coding: utf-8 -*-
{
    'name': 'Informe Emplazamientos',
    'version': '1.0',
    'summary': 'Brief description of the module',
    'description': '''
        Detailed description of the module
    ''',
    'category': 'Uncategorized',
    'depends': ['base', 'sale', 'mp_site'],
    'data': [
        'security/ir.model.access.csv',
        'views/informe_emplazamientos_views.xml',
    ],
    'license': 'LGPL-3',
    'installable': True,
    'application': False,
    'auto_install': False,
}