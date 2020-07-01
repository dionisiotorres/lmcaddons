# -*- coding: utf-8 
from odoo import api, fields, models, _

class EventRegistration(models.Model):
    _inherit = 'event.registration'

    attentees_img = fields.Binary(string='Image')
    img_warning = fields.Char(string="Image Warning")

    @api.model
    def create(self, vals):
        partner = self.env['res.partner'].search([('email', '=', vals['email'])])
        if partner and len(partner) > 1:
            vals['img_warning'] = "Multiple Contact Found for this email"
            vals['attentees_img'] = False
        elif partner:
            vals['attentees_img'] = partner.image
            vals['img_warning'] = False
        else:
            vals['img_warning'] = "Contact not Found"
            vals['attentees_img'] = False
        return super(EventRegistration, self).create(vals)


class CompanyAddButton(models.Model):
    _inherit = 'res.company'

    def commpare_email(self):
        attendees = self.env['event.registration'].search([('email', '!=', False)])
        for attendee in attendees:
            partner = self.env['res.partner'].search([('email', '=', attendee.email)])
            if partner and len(partner) > 1:
                attendee.write({"img_warning": "Multiple Contact Found for this email",
                     'attentees_img': False})
            elif partner:
                attendee.write({"attentees_img": partner.image, 'img_warning': False})
            else:
                attendee.write({"img_warning": "Contact not Found", "attentees_img": False})

