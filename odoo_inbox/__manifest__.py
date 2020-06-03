# -*- coding: utf-8 -*-
#################################################################################
# Author      : Kanak Infosystems LLP. (<http://kanakinfosystems.com/>)
# Copyright(c): 2012-Present Kanak Infosystems LLP.
# All Rights Reserved.
#
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#
# You should have received a copy of the License along with this program.
# If not, see <http://kanakinfosystems.com/license>
#################################################################################

{
    'name': 'Mailbox (Odoo Inbox)',
    'category': 'Website',
    'author': 'Kanak Infosystems LLP.',
    'support': 'info@kanakinfosystems.com',
    'version': '1.3',
    'description':
        """
Mailbox (Odoo Inbox)
========================
        """,
    'depends': ['website', 'mail', 'contacts'],
    'data': [
        'data/data.xml',
        'security/ir.model.access.csv',
        'views/template.xml',
        'views/mail_message.xml'
    ],
    'images': ['static/description/banner.jpg'],
    'installable': True,
    'license': 'OPL-1',
    'bootstrap': True,  # load translations for login screen
    'application': True,
    'price': 150,
    'currency': 'EUR',
    'live_test_url': 'http://68.183.95.144:8090/web?db=odooinbox_v12',
}
