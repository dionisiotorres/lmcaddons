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

import logging
from odoo import api, fields, models
from odoo.http import request
_logger = logging.getLogger(__name__)

class Website(models.Model):
    _inherit = 'website'

    def _get_ad_block_ids(self):
        ad_block_ids = request.env["product.template"].search([('is_ad_block','!=',False),
            ('website_published','!=',False)]) or False
        return ad_block_ids

    def _get_ad_block_image_size(self, block_id):
        size = ''
        pos = block_id and block_id.block_position
        if pos:
            if pos in ["shop_page_full_top", "shop_page_full_bottom", "cart_full_bottom", "confirmation_page_full_bottom","payment_full_bottom"]:
                size = "1140 X 190"
            elif pos in ["below_product_categories"]:
                size = "262 X 190"
            # elif pos in ["home_page_full_top"]:
            #     size = "1286 X 190"
            # elif pos in ["confirmation_page_right_bottom"]:
            #     size = "262 X 244"
            else:
                size = "165 X 244"
        return size
