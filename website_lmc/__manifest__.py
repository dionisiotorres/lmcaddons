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
    'depends': ['website_sale', 'website_form'],
    'data': [
        'views/assets.xml',
        'security/ir.model.access.csv',
        'data/data.xml',
        'views/my_account.xml',
        'views/partner_view.xml',
        #'views/views.xml',
        'views/footer.xml',
        'views/website_login_page.xml',
        'views/lmc_home_template.xml',
        'views/program.xml',
        'views/registration_template.xml',
        'views/run.xml',
        'views/sponsors.xml',
        'views/range.xml',
        'views/fanshop.xml',
        'views/geniessen.xml',
        'views/unterkuenfte.xml',
        'views/gallery.xml',
    ],
    'installable': True,
    'license': 'OPL-1',
    'currency': 'EUR',
}
