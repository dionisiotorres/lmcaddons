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

from odoo import http, _
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager, get_records_pager
from odoo.exceptions import AccessError
from odoo.http import request
from odoo.tools import consteq
import logging
_logger = logging.getLogger(__name__)

class PortalAccount(CustomerPortal):

    def _prepare_portal_layout_values(self):
        values = super(PortalAccount, self)._prepare_portal_layout_values()
        partner = request.env.user.partner_id

        my_ad_blocks_count = request.env['sale.order.line'].search_count([
            ('order_partner_id', '=', partner.id),
            ('is_ad_block_line', '=', True),
        ])
        values['my_ad_blocks_count'] = my_ad_blocks_count
        return values

    # ------------------------------------------------------------
    # My Ad Blocks Ccontract
    # ------------------------------------------------------------

    def _ad_blocks_check_access(self, ad_block_id, access_token=None):
        ad_blocks = request.env['sale.order.line'].browse([ad_block_id])
        ad_blocks_sudo = ad_blocks.sudo()
        try:
            ad_blocks.check_access_rights('read')
            ad_blocks.check_access_rule('read')
        except AccessError:
            if not access_token or not consteq(ad_blocks_sudo.access_token, access_token):
                raise
        return ad_blocks

    def _ad_blocks_get_page_view_values(self, ad_block, access_token, **kwargs):
        values = {
            'page_name': 'website_ad_blocks',
            'ad_block': ad_block,
        }
        if access_token:
            values['no_breadcrumbs'] = True
        if kwargs.get('error'):
            values['error'] = kwargs['error']
        if kwargs.get('warning'):
            values['warning'] = kwargs['warning']
        if kwargs.get('success'):
            values['success'] = kwargs['success']

        history = request.session.get('my_ad_blocks_history', [])
        values.update(get_records_pager(history, ad_block))
        values.update(request.env['payment.acquirer']._get_available_payment_input(ad_block.order_partner_id, ad_block.order_partner_id.company_id))
        return values

    @http.route(['/my/ad/blocks', '/my/ad/blocks/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_ad_blocks(self, page=1, date_begin=None, date_end=None, sortby=None, **kw):
        values = self._prepare_portal_layout_values()
        partner = request.env.user.partner_id
        AdBlocksObj = request.env['sale.order.line']

        domain = [
            ('order_partner_id', '=', partner.id),
            ('is_ad_block_line', '=', True),
        ]

        searchbar_sortings = {
            'create_date': {'label': _('Create Date'), 'order': 'create_date asc'},
            'ad_date_from': {'label': _('Date From'), 'order': 'ad_date_from asc'},
            'ad_date_to': {'label': _('Date To'), 'order': 'ad_date_to asc'},
            'ad_block_status': {'label': _('Block Status'), 'order': 'ad_block_status asc'},
        }
        # default sort by order
        if not sortby:
            sortby = 'create_date'
        order = searchbar_sortings[sortby]['order']

        archive_groups = self._get_archive_groups('sale.order.line', domain)
        if date_begin and date_end:
            domain += [('create_date', '>', date_begin), ('create_date', '<=', date_end)]

        # count for pager
        ad_blocks_count = AdBlocksObj.search_count(domain)

        # make pager
        pager = request.website.pager(
            url="/my/ad/blocks",
            url_args={'date_begin': date_begin, 'date_end': date_end},
            total=ad_blocks_count,
            page=page,
            step=self._items_per_page
        )
        # search the count to display, according to the pager data
        ad_blocks = AdBlocksObj.search(domain, limit=self._items_per_page, offset=pager['offset'])
        request.session['my_ad_blocks_history'] = ad_blocks.ids[:100]

        values.update({
            'date': date_begin,
            'ad_blocks_obj': ad_blocks.sudo(),
            'pager': pager,
            'archive_groups': archive_groups,
            'default_url': '/my/ad/blocks',
            'page_name': 'ad_blocks_contracts',
            'searchbar_sortings': searchbar_sortings,
            'sortby': sortby,
        })
        return request.render("website_advertisement_manager.portal_my_ad_blocks", values)

    @http.route(['/my/ad/blocks/<int:ad_block_id>'], type='http', auth="user", website=True)
    def portal_my_ad_block_detail(self, ad_block_id=None, access_token=None, **kw):
        ad_b = request.env['sale.order.line'].browse([ad_block_id])
        if not ad_b.exists():
            return request.render('website.404')
        try:
            ad_block_sudo = self._ad_blocks_check_access(ad_block_id, access_token)
        except AccessError:
            return request.redirect('/my')
        values = self._ad_blocks_get_page_view_values(ad_block_sudo, access_token, **kw)
        return request.render("website_advertisement_manager.portal_my_ad_block_page", values)
