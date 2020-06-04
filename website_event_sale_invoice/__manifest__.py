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
    'name': 'Website Event Sale Invoice',
    'description': 'Website Event Sale Invoice',
    'category': 'Event',
    'version': '1.0',
    'author': 'Kanak Infosystems LLP.',
    'website': 'http://www.kanakinfosystems.com',
    'depends': ['website_event', 'payment_transfer', 'sale', 'account'],
    'data': [
        'views/event_views.xml',
    ],
    'installable': True,
    'application': False,
    'support': 'info@kanakinfosystems.com',
}
