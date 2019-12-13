# -*- coding: utf-8 -*-

{
    'name': 'Website LMC',
    'version': '1.0',
    "summary": 'Website LMC',
    'description': """Website LMC""",
    'category': 'Website',
    'author': 'Kanak Infosystems LLP.',
    'website': 'http://www.kanakinfosystems.com',
    'images': ['static/description/banner.jpg'],
    'depends': ['website_sale'],
    'data': [
        'views/assets.xml',
        'security/ir.model.access.csv',
        'data/data.xml',
        'views/my_account.xml',
        'views/partner_view.xml',
        'views/footer.xml',
        'views/website_login_page.xml',
        'views/lmc_home_template.xml',
    ],
    'installable': True,
    'license': 'OPL-1',
    'currency': 'EUR',
}
