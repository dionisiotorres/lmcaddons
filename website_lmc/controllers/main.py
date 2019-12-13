# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo.http import request, route
from odoo.addons.portal.controllers.portal import CustomerPortal
import base64


class CustomerUserPortal(CustomerPortal):

    OPTIONAL_BILLING_FIELDS = ["zipcode", "state_id", "vat", "company_name", "about_us", "x_family_name", "x_gender",
    "x_birthdate", "x_nationality", "x_drive_club", "x_driver_license_type", "x_driver_license_num", "x_driver_pict_path",
    "x_driver_success", "x_driver_year_racing_since", "x_driver_amount_events", "x_driver_year_last_event",
    "x_driver_year_driving_license_issuance", "x_driver_shirt_size"]

    @route(['/my/account'], type='http', auth='user', website=True)
    def account(self, redirect=None, **post):
        partner = request.env.user.partner_id
        if 'clear_image' in post:
            partner.write({'image': False})
            post.pop('clear_image')
            if 'ufile' in post:
                post.pop('ufile')
        elif 'ufile' in post:
            if post.get('ufile'):
                image = post.get('ufile').read()
                partner.write({'image': base64.b64encode(image), 'about_us': post.get('about_us') or ''})
            post.pop('ufile')
        res = super(CustomerUserPortal, self).account(redirect=redirect, **post)
        return res

    @route(['/my', '/my/home'], type='http', auth="user", website=True)
    def home(self, redirect=None, **kw):
        values = self._prepare_portal_layout_values()
        partner = request.env.user.partner_id

        values.update({
            'error': {},
            'error_message': [],
        })

        if kw and request.httprequest.method == 'POST':
            error, error_message = self.details_form_validate(kw)
            values.update({'error': error, 'error_message': error_message})
            values.update(kw)
            if not error:
                values = {key: kw[key] for key in self.MANDATORY_BILLING_FIELDS}
                values.update({key: kw[key] for key in self.OPTIONAL_BILLING_FIELDS if key in kw})
                values.update({'country_id': int(values.pop('country_id', 0))})
                values.update({'zip': values.pop('zipcode', '')})
                if values.get('state_id') == '':
                    values.update({'state_id': False})
                partner.sudo().write(values)
                if redirect:
                    return request.redirect(redirect)
                return request.redirect('/my/home')

        countries = request.env['res.country'].sudo().search([])
        states = request.env['res.country.state'].sudo().search([])

        shippings = partner.mapped('child_ids').filtered(lambda r: r.type == 'delivery')
        others = partner.mapped('child_ids').filtered(lambda r: r.type == 'other')
        # import pdb
        # pdb.set_trace()
        # shippings = request.env['res.partner'].sudo().search([
        #     ("id", "child_of", partner.commercial_partner_id.ids),
        #     ("type", "in", ["delivery"])], order='id desc')
        # others = request.env['res.partner'].sudo().search([
        #     ("id", "child_of", partner.commercial_partner_id.ids),
        #     ("type", "in", ["other"]), ("id", "!=", partner.id)], order='id desc')

        values.update({
            'shippings': shippings,
            'others': others,
            'partner': partner,
            'countries': countries,
            'states': states,
        })
        return request.render("portal.portal_my_home", values)

    # Add new address
    @route(['/account/address'], type='http', auth='user', website=True)
    def shipping_address_form(self, **post):
        actual_partner = request.env.user.partner_id
        Partner = request.env['res.partner'].sudo()
        Country = request.env['res.country'].sudo()
        State = request.env['res.country.state'].sudo()

        if post.get('submitted'):
            if post.get('partner_id'):
                partner = Partner.browse(int(post.get('partner_id')))
                vals = {
                    'name': post.get('name'),
                    'email': post.get('email'),
                    'vat': post.get('vat'),
                    'phone': post.get('phone'),
                    'street': post.get('street'),
                    'city': post.get('city'),
                    'type': post.get('type'),
                    'zip': post.get('zipcode'),
                }

                # If country and state come post post data
                if post.get('country_id') and post.get('country_id') != '':
                    vals.update({
                        'country_id': int(post.get('country_id'))
                    })
                if post.get('state_id') and post.get('state_id') != '':
                    vals.update({
                        'state_id': int(post.get('state_id'))
                    })
                # Few countries does not have state so remove old state
                if vals.get('country_id') and vals.get('state_id'):
                    state = State.browse(vals.get('state_id'))
                    if state.country_id.id != vals.get('country_id'):
                        vals.update({'state_id': None})

                partner.write(vals)
                return request.redirect('/my/home')
            else:
                # New create address
                vals = {
                    'name': post.get('name'),
                    'email': post.get('email'),
                    'vat': post.get('vat'),
                    'phone': post.get('phone'),
                    'street': post.get('street'),
                    'city': post.get('city'),
                    'type': post.get('type'),
                    'zip': post.get('zipcode'),
                }

                # If country and state come post post data
                if post.get('country_id') and post.get('country_id') != '':
                    vals.update({
                        'country_id': int(post.get('country_id'))
                    })
                if post.get('state_id') and post.get('state_id') != '':
                    vals.update({
                        'state_id': int(post.get('state_id'))
                    })
                # Few countries does not have state so remove old state
                if vals.get('country_id') and vals.get('state_id'):
                    state = State.browse(vals.get('state_id'))
                    if state.country_id.id != vals.get('country_id'):
                        vals.update({'state_id': None})

                actual_partner.child_ids = [[0, 0, vals]]
                return request.redirect('/my/home')

        # request for old address update or create new

        if post.get('partner_id'):
            partner_id = int(post.get('partner_id'))
            if partner_id in actual_partner.child_ids.ids or partner_id == actual_partner.id:
                values = Partner.browse(partner_id)
                country = 'country_id' in values and values['country_id'] != '' \
                    and request.env['res.country'].browse(int(values['country_id']))
                country = country and country.exists()
                render_values = {
                    'partner': values,
                    'country': country,
                    'countries': country.get_website_sale_countries(),
                    'states': country.get_website_sale_states(),
                    'type': values.type,
                }
                return request.render("website_lmc.add_profile_shipping_address", render_values)
            else:
                request.redirect('/my/home')
        else:
            render_values = {
                'partner': {},
                'countries': Country.get_website_sale_countries(),
                'states': Country.get_website_sale_states(),
                'type': post.get('type'),
            }
            return request.render("website_lmc.add_profile_shipping_address", render_values)

    @route(["/partner/delete"], type="json", auth="user", website=True)
    def partner_delete(self, partner_id=None, **post):
        Partner = request.env['res.partner'].sudo()
        if partner_id:
            partner = Partner.browse(partner_id)
            partner.write({'active': False})
        return {"success": True}

    # edit vehicle info
    @route(['/vehicle/info'], type='http', auth='user', website=True)
    def vehicle_info_form(self, **post):
        partner = request.env.user.partner_id
        values = {
            "partner": partner,
        }
        return request.render("website_lmc.edit_vehicle_information", values)

    @route(["/vehicle/info/edit"], type="http", auth="user", website=True)
    def vehicle_info_edit(self, **post):
        partner = request.env.user.partner_id
        vals = {
            'x_vehicle_pict': post.get('x_vehicle_pict'),
            'x_vehicle_cat': post.get('x_vehicle_cat'),
            'x_vehicle_manufacturer': post.get('x_vehicle_manufacturer'),
            'x_vehicle_type': post.get('x_vehicle_type'),
            'x_vehicle_ccm': post.get('x_vehicle_ccm'),
            'x_vehicle_year_construction': post.get('x_vehicle_year_construction'),
            'x_vehicle_approved': post.get('x_vehicle_approved'),
            'x_vehicle_cylinder': post.get('x_vehicle_cylinder'),
            'x_vehicle_horse_power': post.get('x_vehicle_horse_power'),
            'x_vehicle_desc': post.get('x_vehicle_desc'),
            'x_vehicle_modifications': post.get('x_vehicle_modifications'),
            'x_vehicle_tire_size': post.get('x_vehicle_tire_size'),
            'x_vehicle_rim_size': post.get('x_vehicle_rim_size'),
            'x_vehicle_doc_number': post.get('x_vehicle_doc_number'),
            'x_registrasion_number': post.get('x_registrasion_number'),
            'x_vehicle_pict_path': post.get('x_vehicle_pict_path'),
            'x_vehicle_homologation_num': post.get('x_vehicle_homologation_num'),
            'x_race_info_pit_id': post.get('x_race_info_pit_id'),
            'x_vehicle_number_plate': post.get('x_vehicle_number_plate'),
        }
        # Vehicle information update

        partner.write(vals)
        return request.redirect('/my/home')
