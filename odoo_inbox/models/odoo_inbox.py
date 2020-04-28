# -*- coding: utf-8 -*-
import odoo
from odoo import api, fields, models, _

class OdooInbox(models.AbstractModel):
    _name = 'odoo.inbox'

    @api.multi
    def set_done(self, message=None):
        message.message_label = 'done'

    @api.multi
    def set_star(self, action=None, message=None):
        message.message_label = 'starred' if action == 'add' else 'inbox'

    @api.multi
    def move_to_send(self, action=None, message=None):
        message.message_label = 'sent' if action == 'add' else 'inbox'

    @api.multi
    def move_to_trash(self, message=None):
        message.message_label = 'trash'

