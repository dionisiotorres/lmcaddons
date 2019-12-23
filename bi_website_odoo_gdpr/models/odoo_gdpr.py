# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from itertools import groupby
from datetime import datetime, timedelta

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools import float_is_zero, float_compare, DEFAULT_SERVER_DATETIME_FORMAT
from odoo.tools.misc import formatLang
from odoo.tools import html2plaintext
from odoo.tools.translate import html_translate
import odoo.addons.decimal_precision as dp


class GDPRTemplate(models.Model):
    _name = 'gdpr.template'
    _description = 'GDPR Template'

    name = fields.Char('Name')
    description = fields.Text('Description')
    url = fields.Char('Redirect URL')
    selection_type = fields.Selection([('user','User'),('address','Address')],string="Type",default="user")
    active = fields.Boolean(string='Active',default=True)
    image = fields.Binary(string='Image')


class GDPRRequest(models.Model):
    _name = 'gdpr.request'
    _description = 'GDPR Request'
    _order = 'create_date desc'

    name = fields.Char('Name')
    partner_id = fields.Many2one('res.partner',string='Res Partner',)
    gdpr_id = fields.Many2one('gdpr.template',string='Gdpr Template',)
    selection_type = fields.Selection([('s_obj','Specific Object'),('all_obj','All Object')],string="Operation For",default="user")
    request_type = fields.Selection([('download','Download'),('delete','Delete')],string="Request Type",default="user")
    state =  fields.Selection([('pending','Pending'),('done','Done'),('cancel','Cancel')],string="Request Type",default="user")
    create_date = fields.Datetime('Created On')
    is_wipe = fields.Boolean('Is data wiped ??',readonly=True, default=False)

    @api.multi
    def mark_done(self):
        for request in self:
            if request.request_type == 'delete':
                request.wipe_data()
            request.write({'state' : 'done'})
        return True

    @api.multi
    def mark_cancel(self):
        for request in self:            
            request.write({'state' : 'cancel',})

        return True

    @api.multi
    def wipe_data(self):
        for request in self:
            if request.partner_id:
                request.partner_id.write({
                    'phone' : str('N/a'),
                    'email' : str('N/a'),
                    'street' : str('N/a'),
                    'street2' : str('N/a'),
                    'zip' : str('N/a'),
                    'city' : str('N/a'),
                    'state_id' : False,
                    'country_id' : False,
                    'mobile' : str('N/a'),
                    })
                request.write({'is_wipe' : True})
            else:
                UserError(_('Partner Is missing !!!'))

        return True


class GDPRConfiguration(models.Model):
    _name = 'gdpr.config'
    _description = 'GDPR Configuration'

    name = fields.Char('Name')
    title = fields.Char('GDPR Title')
    description = fields.Html('Description')
    remove_msg = fields.Html('Removal Message')
    is_gdpr_msg = fields.Boolean('Allow GDPR Message')
    gdpr_msg = fields.Text('GDPR Message')


    @api.model
    def default_get(self, fields):
        res = super(GDPRConfiguration, self).default_get(fields)
        config_id = self.env['gdpr.config'].sudo().search([],order="id desc", limit=1)
        if config_id:
            res.update({
                'name' : config_id.name,
                'title' : config_id.title,
                'description' : config_id.description,
                'remove_msg' : config_id.remove_msg,
                'is_gdpr_msg' : config_id.is_gdpr_msg,
                'gdpr_msg' : config_id.gdpr_msg,
                })
            return res
        else:
            return res


    def save(self):
        for config in self:
            vals = {
            'name' : config.name,
            'title' : config.title,
            'description' : config.description,
            'remove_msg' : config.remove_msg,
            'is_gdpr_msg' : config.is_gdpr_msg,
            'gdpr_msg' : config.gdpr_msg,
            }
            config.sudo().write(vals)
        return {'type': 'ir.actions.act_window_close'}
