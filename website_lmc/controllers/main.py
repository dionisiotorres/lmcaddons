
# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import http, _
from odoo.http import request, route
from odoo.addons.portal.controllers.portal import CustomerPortal
from odoo.addons.website.controllers.main import Website
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
from odoo.exceptions import UserError
from datetime import datetime
import base64


class CustomWebsiteHome(Website):
    @http.route('/', type='http', auth="public", website=True)
    def index(self, **kw):
        res = super(CustomWebsiteHome, self).index(**kw)
        boxes = request.env['home.boxes'].sudo().search([])
        res.qcontext['home_boxes'] = boxes
        return res

class CustomerUserPortal(CustomerPortal):

    OPTIONAL_BILLING_FIELDS = ["zipcode", "state_id", "vat", "company_name", "about_us", "x_family_name", "x_gender",
    "x_birthdate", "x_nationality", "x_drive_club", "x_driver_license_type", "x_driver_license_num", "x_driver_pict_path",
    "x_driver_success", "x_driver_year_racing_since", "x_driver_amount_events", "x_driver_year_last_event",
    "x_driver_year_driving_license_issuance", "x_driver_shirt_size", "account_type_id", "account_number", "account_details"]

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
        if post.get('x_birthdate'):
            try:
                my_date = datetime.strptime(post.get('x_birthdate'), '%m-%d-%Y')
                birthday_date = my_date.strftime(DEFAULT_SERVER_DATE_FORMAT)
                post['x_birthdate'] = birthday_date
            except:
                raise UserError(_("Please Enter correct birth date."))
        else:
            post['x_birthdate'] = False

        res = super(CustomerUserPortal, self).account(redirect=redirect, **post)
        res.qcontext['tabinfo'] = 'personal_data'
        license_type = request.env['driver.license.codes'].sudo().search([])
        nationalities = request.env['res.country'].sudo().search([])
        shirt_size_ids = request.env['shirt.size.codes'].sudo().search([])
        account_type_ids = request.env['account.type'].sudo().search([])
        res.qcontext['license_types'] = license_type
        res.qcontext['nationalities'] = nationalities
        res.qcontext['shirt_size_ids'] = shirt_size_ids
        res.qcontext['account_type_ids'] = account_type_ids
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
                return request.redirect('/my/home?tabinfo=personal_data')

        countries = request.env['res.country'].sudo().search([])
        states = request.env['res.country.state'].sudo().search([])

        shippings = partner.mapped('child_ids').filtered(lambda r: r.type == 'delivery')
        others = partner.mapped('child_ids').filtered(lambda r: r.type == 'other')
        values.update({
            'shippings': shippings,
            'others': others,
            'partner': partner,
            'countries': countries,
            'states': states,
            'tabinfo': 'personal_data',
        })
        if kw.get('tabinfo'):
            values['tabinfo'] = kw.get('tabinfo')
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
        vehicle_code = request.env['vehicle.code'].sudo().search([])
        values = {
            'partner': partner,
            'tabinfo': 'vehicle',
            'vehicle_categories': vehicle_code
        }
        return request.render("website_lmc.edit_vehicle_information", values)

    @route(["/vehicle/info/edit"], type="http", auth="user", website=True)
    def vehicle_info_edit(self, **post):
        partner = request.env.user.partner_id
        # import pdb;pdb.set_trace()
        # Vehicle information update
        vals = {
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
            'chassis_no': post.get('chassis_no'),
            'vehicle_code': post.get('x_vehicle_cat'),
        }
        if 'clear_image' in post:
            vals.update({'x_vehicle_pict': False})
            post.pop('clear_image')
            if 'vehicle_img' in post:
                post.pop('vehicle_img')
        elif 'vehicle_img' in post:
            if post.get('vehicle_img'):
                image = post.get('vehicle_img').read()
                vals.update({'x_vehicle_pict': base64.b64encode(image)})
            post.pop('vehicle_img')
        partner.write(vals)

        partner.write(vals)
        return request.redirect("/my/home?tabinfo=vehicle")

    # edit nomination info
    @route(['/nomination/info'], type='http', auth='user', website=True)
    def nomination_info_form(self, **post):
        partner = request.env.user.partner_id
        values = {
            "partner": partner,
            "tabinfo": 'nomination',
        }
        return request.render("website_lmc.edit_nomination_information", values)

    @route(["/nomination/info/edit"], type="http", auth="user", website=True)
    def nominatio_info_edit(self, **post):
        partner = request.env.user.partner_id
        # Vehicle information update
        vals = {
            'x_nomination_year': post.get('x_nomination_year'),
            # 'x_race_info_field': post.get('x_race_info_field'),
            # 'x_date_enrolement_reveived': post.get('x_date_enrolement_reveived'),
            'x_nomination_status': post.get('x_nomination_status'),
            'x_race_info_starting_num': post.get('x_race_info_starting_num'),
            'x_pit_box_number': post.get('x_pit_box_number'),
            'x_vehicle_inspection_passed': post.get('x_vehicle_inspection_passed'),
            'x_autorized': post.get('x_autorized'),
            'x_vehicle_approved': post.get('x_vehicle_approved'),
            'x_race_info_pit_id': post.get('x_race_info_pit_id'),
            'x_vehicle_desc': post.get('x_vehicle_desc'),
        }
        partner.write(vals)
        return request.redirect('/my/home?tabinfo=nomination')

    @route(["/profile/image/save"], type="json", auth="user", website=True)
    def profile_img_save(self, **post):
        partner_id = request.env.user.partner_id
        if post.get('data'):
            partner_id.image = post.get('data')[22:]
        return {"success": True}

    @route(["/profile/image/delete"], type="json", auth="user", website=True)
    def profile_img_delete(self, **post):
        partner_id = request.env.user.partner_id
        partner_id.image = ''
        return {"success": True}

    @route(["/racefields"], type="http", auth="public", website=True)
    def racefields(self, **post):
        rennfelder_ids = request.env['rennfelder'].search([])
        partner_ids = request.env['res.partner'].sudo().search([], order='x_race_info_starting_num')
        partner_id = request.env.user.partner_id
        selected_type = partner_id.x_race_info_field.id if partner_id.x_race_info_field else False
        values = {'rennfelder_ids': rennfelder_ids,
                  'partner_ids': partner_ids,
                  'company': request.env.user.company_id,
                  'selected_type': selected_type}
        return request.render("website_lmc.racefields_lmc", values)

    @route(["/partner/car/info"], type="json", auth="public", website=True)
    def partner_car_info(self, **post):
        values = {'modeldata': False}
        if post.get('partner_id'):
            partner = request.env['res.partner'].sudo().search([('id', '=', int(post.get('partner_id')))])
            values['modeldata'] = request.env['ir.ui.view'].render_template("website_lmc.modal_popup_car_desc", {'partner_id': partner})
        return values
