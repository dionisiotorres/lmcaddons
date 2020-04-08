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

from odoo import http
from odoo.http import request
from odoo.addons.website_sale.controllers.main import WebsiteSale
from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta
import logging
_logger = logging.getLogger(__name__)

class WebsiteAdvertisement(http.Controller):

    @http.route(['/advertisement'], type='http', auth='public', website=True,)
    def advertisement(self, **kwargs):
        ad_block_ids = request.env["product.template"].search([('is_ad_block','!=',False),
            ('website_published','!=',False)])
        values = {
            'ad_block_ids': ad_block_ids.sudo(),
        }
        return request.render("website_advertisement_manager.website_ad_blocks_page", values)

    @http.route(['/book/ad/block'], type='json', auth='public', website=True,)
    def book_ad_block(self, block_id):
        block_id = request.env['product.template'].browse(block_id)

        # Returns disabledDates list
        order_lines = request.env['sale.order.line'].sudo().search([
            ('product_id','=', block_id.product_variant_id.id),
            ('is_ad_block_line','=',True),
            ('ad_block_status', '!=', 'expire'),
        ])
        block_date_list = []
        if order_lines:
            for line in order_lines:
                block_date_list += line._get_date_list(line.ad_date_from, line.ad_date_to)
            block_date_list = list(set(block_date_list))

        block_date_list = [str(d) for d in block_date_list]
        values = {
            'block': block_id,
            'block_date_list': block_date_list or []
        }
        values['website_advertisement_manager.website_ad_block_book_modal'] = request.env['ir.ui.view'].render_template("website_advertisement_manager.website_ad_block_book_modal", values)
        return values

    @http.route(['/set/block/banner'], method=['POST'], type='json', auth='public', website=True,)
    def set_block_banner(self, block_id, image=None, ad_banner_link=None, ad_img_name=None, **kw):
        block_line = request.env['sale.order.line'].sudo().browse(block_id)
        if block_line:
            block_line.ad_display_type = "banner"
            if image:
                block_line.ad_banner_img = image
            if ad_banner_link:
                block_line.ad_banner_link = ad_banner_link or ''
            if ad_img_name:
                block_line.ad_img_name = ad_img_name
            block_line.ad_content_set_pending()
        return

    @http.route(['/validate/ad/dates'], method=['POST'], type='json', auth='public', website=True,)
    def validate_ad_dates(self, block_id, ad_date_from, ad_date_to, **kw):
        data = {'error':0, 'error_msg' : ''}
        try:
            ad_date_from = datetime.strptime(ad_date_from,"%m/%d/%Y").date()
            ad_date_to = datetime.strptime(ad_date_to,"%m/%d/%Y").date()
        except:
            data = {
                'error': 1,
                'error_msg': 'Entered date is not valid'
            }
            return data

        # validate for date before today
        d3 = date.today()
        rd1 = relativedelta(d3,ad_date_from)
        rd2 = relativedelta(d3,ad_date_to)
        if rd1.days > 0 or rd1.months > 0 or rd1.years > 0 or rd2.days > 0 or rd2.months > 0 or rd2.years > 0:
            data = {
                'error': 1,
                'error_msg': 'Date Should be after Today'
            }
            return data

        if ad_date_to < ad_date_from:
            data = {
                'error': 1,
                'error_msg': 'Date To must be less than Date From'
            }
            return data

        # list of all dates of this block
        block_id = request.env['product.product'].browse(int(block_id))

        # Returns disabledDates list
        order_lines = request.env['sale.order.line'].sudo().search([('product_id','=', block_id.id),
            ('is_ad_block_line','=',True),('ad_block_status', '!=', 'expire')])

        block_date_list = []
        if order_lines:
            for line in order_lines:
                block_date_list += line._get_date_list(line.ad_date_from, line.ad_date_to)
            block_date_list = list(set(block_date_list))

        # list of dates of current line block
        curr_date_list = []
        delta = ad_date_to - ad_date_from
        for i in range(delta.days + 1):
            curr_date_list.append(ad_date_from + timedelta(days=i))
        # check for duplicates
        if block_date_list and curr_date_list:
            if any( date in block_date_list for date in curr_date_list):
                data = {
                    'error': 1,
                    'error_msg': 'This slot time is not available for this block.'
                }
                return data

        return data


class WebsiteSale(WebsiteSale):

    def _get_search_domain(self, search, category, attrib_values):
        res = super(WebsiteSale, self)._get_search_domain(search, category, attrib_values)
        res.append(('is_ad_block', '=', False))
        return res

    @http.route(['/shop/cart/update'], type='http', auth="public", methods=['POST'], website=True, csrf=False)
    def cart_update(self, product_id, add_qty=1, set_qty=0, **kw):
        product_id = request.env['product.product'].browse(int(product_id))
        if product_id and product_id.is_ad_block:
            ad_vals = {
                'ad_date_to' : datetime.strptime(kw.get("ad_date_to"),"%m/%d/%Y").date(),
                'ad_date_from' : datetime.strptime(kw.get("ad_date_from"),"%m/%d/%Y").date(),
            }
            product_custom_attribute_values = None
            if kw.get('product_custom_attribute_values'):
                product_custom_attribute_values = json.loads(kw.get('product_custom_attribute_values'))
            request.website.sale_get_order(force_create=1).with_context(ad_vals=ad_vals)._cart_update(
                product_id=int(product_id),
                add_qty=float(add_qty),
                set_qty=float(set_qty),
                product_custom_attribute_values=product_custom_attribute_values,
            )
            so = request.website.sale_get_order()
            line = so.order_line.filtered(lambda l: l.is_ad_block_line and l.product_id.id == int(product_id))
            if line:
                line.product_uom_qty = line.ad_total_days
            return request.redirect("/shop/cart")
        res = super(WebsiteSale, self).cart_update(product_id, add_qty, set_qty, **kw,)
        return res
