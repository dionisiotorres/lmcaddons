# -*- coding: utf-8 -*-
#################################################################################
# Author      : Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# Copyright(c): 2015-Present Webkul Software Pvt. Ltd.
# License URL : https://store.webkul.com/license.html/
# All Rights Reserved.
#
#
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#
# You should have received a copy of the License along with this program.
# If not, see <https://store.webkul.com/license.html/>
#################################################################################

from odoo import api, fields, models, _
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    auto_approve_ad_block = fields.Boolean(
        "Auto Approve Ad Block",
        help="Ad Block will be automatically approved",
    )

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        IRDefault = self.env['ir.default'].sudo()
        res.update({
            'auto_approve_ad_block': IRDefault.get(
                'res.config.settings', 'auto_approve_ad_block'),
        })
        return res

    @api.multi
    def set_values(self):
        super(ResConfigSettings, self).set_values()
        IRDefault = self.env['ir.default'].sudo()
        IRDefault.set('res.config.settings', 'auto_approve_ad_block', self.auto_approve_ad_block)
        return True
