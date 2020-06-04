# -*- coding: utf-8 -*-
from odoo import fields, models


class EventEvent(models.Model):
    _inherit = 'event.event'

    online_auto_invoice = fields.Boolean(string='Online Automatic Invoice', help='Create invoice online after successfull payment.')
