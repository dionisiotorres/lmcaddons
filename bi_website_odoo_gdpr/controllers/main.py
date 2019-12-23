# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.


import base64

from odoo import http
from werkzeug.exceptions import Forbidden, NotFound
from odoo import fields, http, tools, _
from odoo.http import request
from odoo.exceptions import ValidationError
from odoo.osv import expression
from datetime import timedelta, datetime
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager


class customerprofile(CustomerPortal):

    def _prepare_portal_layout_values(self):
        values = super(customerprofile, self)._prepare_portal_layout_values()

        requests = request.env['gdpr.request']
        partner = request.env.user.partner_id
        request_count = requests.sudo().search_count([('partner_id','=',partner.id)])

        values.update({
            'request_count': request_count,
        })

        return values

    @http.route(['/gdpr/profile', '/gdpr/profile/page/<int:page>'], type='http', auth="public", website=True)
    def gdpr_profile(self, page=1, date_begin=None, date_end=None, **kwargs):
        values = self._prepare_portal_layout_values()
        partner = request.env.user.partner_id
        values = {}
        domain = []
        
        
        gpdr_template_obj = request.env['gdpr.template']
        gpdr_request_obj = request.env['gdpr.request']
        gpdr_config_obj = request.env['gdpr.config']

        domain += [('partner_id','=',partner.id)]

        request_count = gpdr_request_obj.sudo().search_count(domain)

        pager = request.website.pager(
            url="/gdpr/profile",
            url_args={'date_begin': date_begin, 'date_end': date_end},
            total=request_count,
            page=page,
            step=self._items_per_page
        )


        gpdr_config_id = gpdr_config_obj.sudo().search([],order="id desc", limit=1)
        gpdr_template_id = gpdr_template_obj.sudo().search([('active','=',True)])
        gpdr_request_id = gpdr_request_obj.sudo().search(domain, limit=self._items_per_page, offset=pager['offset'])


        values.update({
            'partner' : partner,
            'gpdr_config_id' : gpdr_config_id,
            'gpdr_template_id' : gpdr_template_id,
            'gpdr_request_id' : gpdr_request_id,
            'pager': pager,
            'kwargs' : kwargs,
            'request_count' : request_count,
            })

        return request.render("bi_website_odoo_gdpr.bi_gdpr_profile_data",values)


    @http.route(['/my/download'], type='json', auth="user", website=True)
    def snap_download(self, access_token=None, **kw):
        record_id = kw.get('res_id')
        if record_id:
            request_obj = request.env['gdpr.request']

            record_obj = request.env['gdpr.template']
            record_id = record_obj.sudo().browse(int(record_id))

            partner = request.env.user.partner_id
            
            values = {
                'name' : partner.name,
                'partner_id' : partner.id,
                'gdpr_id' : record_id.id,
                'selection_type' : 's_obj', 
                'request_type' : 'download',
                'state' : 'pending',
                'create_date' : datetime.now(),
            }
            request_obj.sudo().create(values)
            return True

    @http.route(['/my/deleted'], type='json', auth="user", website=True)
    def snap_delete(self, access_token=None, **kw):
        record_id = kw.get('res_id')
        if record_id:
            request_obj = request.env['gdpr.request']

            record_obj = request.env['gdpr.template']
            record_id = record_obj.sudo().browse(int(record_id))

            partner = request.env.user.partner_id
            
            values = {
                'name' : partner.name,
                'partner_id' : partner.id,
                'gdpr_id' : record_id.id,
                'selection_type' : 's_obj', 
                'request_type' : 'delete',
                'state' : 'pending',
                'create_date' : datetime.now(),
            }

            request_obj.sudo().create(values)
            return True



    def _order_check_access(self, gdpr_request, access_token=None):
        order = request.env['res.partner'].sudo().browse([gdpr_request])
        order_sudo = order.sudo()
        try:
            order.check_access_rights('read')
            order.check_access_rule('read')
        except AccessError:
            if not access_token or not consteq(order_sudo.access_token, access_token):
                raise
        return order_sudo
        
    @http.route(['/my/data/pdf/<int:gdpr_request>'], type='http', auth="public", website=True)
    def portal_job_order_report(self, gdpr_request, access_token=None, **kw):
        try:
            order_sudo = self._order_check_access(gdpr_request, access_token)
        except AccessError:
            return request.redirect('/my')

        pdf = request.env.ref('bi_website_odoo_gdpr.website_res_partner_report_id').sudo().render_qweb_pdf([order_sudo.id])[0]
        pdfhttpheaders = [
            ('Content-Type', 'application/pdf'),
            ('Content-Length', len(pdf)),
        ]
        return request.make_response(pdf, headers=pdfhttpheaders)