# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    'name': 'Website Event Question Open Ended',
    'summary': 'Ask open ended questions during website event registration',
    'version': '11.0.1.0.0',
    'author': 'Camptocamp, Odoo Community Association (OCA)',
    'license': 'AGPL-3',
    'category': 'Others',
    'depends': [
        'website_event_questions',
    ],
    'website': 'http://www.camptocamp.com',
    'data': [
        'security/ir.model.access.csv',
        'views/event_templates.xml',
        'views/event_views.xml',
    ],
    'demo': [
        'demo/event_demo.xml',
    ],
}
