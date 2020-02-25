# -*- coding: utf-8 -*-

from odoo import models, fields, api
import datetime


class ResPartner(models.Model):
    _inherit = "res.partner"
    _description = 'Contact'

    @api.depends('event_registration_ids.state')
    def _compute_state(self):
        for partner in self:
            event = self.env['event.event'].search([('registration_ids.partner_id', '=', partner.id)], limit=1)
            event_registration_state = event.registration_ids.filtered(lambda a: a.partner_id == partner)
            partner.state = 'draft'
            for event_rec in event_registration_state:
                if event_rec:
                    if event_rec.state == 'draft':
                        partner.state = 'registered'
                    elif event_rec.state == 'open':
                        partner.state = 'confirmed'
                    elif event_rec.state == 'done':
                        partner.state = 'attended'
                    elif event_rec.state == 'cancel':
                        partner.state = 'rejected'
            

    @api.depends('state', 'x_nom_waitlist', 'x_doc_approval', 'x_tech_approval', 'x_nom_qualified')
    def _compute_x_nom_dat(self):
        for record in self:
            # if record.state=='registered':
            #     record.x_nom_registered_dat = datetime.datetime.now()
            # if record.state == 'confirmed':
            #     record.x_nom_confirmed_dat = datetime.datetime.now()
            # if record.state == 'rejected':
            #     record.x_nom_rejected_dat = datetime.datetime.now()
            if record.x_nom_waitlist:
                record.x_nom_waitlist_dat = datetime.datetime.now()
            if record.x_doc_approval:
                record.x_doc_approval_dat = datetime.datetime.now()
            if record.x_tech_approval:
                record.x_tech_approval_dat = datetime.datetime.now()
            if record.x_nom_qualified:
                record.x_nom_qualified_dat = datetime.datetime.now()

    # @api.depends('x_nom_rejected')
    # def _compute_x_nom(self):
    #     for record in self:
    #         if record.x_nom_rejected:
    #             record.x_nom_confirmed = record.x_nom_waitlist = record.x_doc_approval = record.x_tech_approval = record.x_nom_qualified = False

    about_us = fields.Text("About Us")
    # personal inf
    # x_driver_pic = fields.Binary(string='Drive Picture')
    x_family_name = fields.Char(string='Family Name')
    x_gender = fields.Selection([('male', 'Male'), ('female', 'Female')], string='Gender')
    x_birthdate = fields.Date(string='Date of birth')
    x_nationality = fields.Many2one('res.country', string='Nationality')
    x_drive_club = fields.Char(string='Drive Club')
    x_driver_license_type = fields.Many2one('driver.license.codes', string='License Type')
    x_driver_license_num = fields.Char(string='License Number')
    x_driver_pict_path = fields.Char(string='Path to picture of the driver')
    x_driver_success = fields.Text(string='Successes of the driver')
    x_driver_year_racing_since = fields.Integer(string='Racing since')
    x_driver_amount_events = fields.Integer(string='# of races participated')
    x_driver_year_last_event = fields.Integer(string='Driver year of last event')
    x_driver_year_driving_license_issuance = fields.Integer(string='Year of issuance of driving license')
    x_driver_shirt_size = fields.Many2one('shirt.size.codes', string='Drivers shirt size')
    # vehical info
    x_vehicle_pict = fields.Binary(string='Vehicle picture')
    x_vehicle_cat = fields.Many2one('vehicle.code', string='Vehicle Category')
    x_vehicle_manufacturer = fields.Char(string='Vehicle manufacturer')
    x_vehicle_type = fields.Char(string='Vehicle Type')
    x_vehicle_ccm = fields.Integer(string='Vehicle ccm')
    x_vehicle_year_construction = fields.Integer(string='Vehicle year of construction')
    x_vehicle_approved = fields.Boolean(string='Vehicle approved?')
    x_vehicle_cylinder = fields.Integer(string='Vehicle number of cylinders')
    x_vehicle_horse_power = fields.Integer(string='Vehicle horse power')
    x_vehicle_desc = fields.Char(string='Vehicle description')
    x_vehicle_modifications = fields.Char(string='Vehicle modifications')
    x_vehicle_tire_size = fields.Char(string='Vehicle tire size')
    x_vehicle_rim_size = fields.Char(string='Vehicle rim size')
    x_vehicle_doc_number = fields.Char(string='Vehicle document (FIA)')
    x_registrasion_number = fields.Char(string='Vehicle FIA registrasion number')
    x_vehicle_pict_path = fields.Char(string='Vehicle Bild-Name')
    x_vehicle_homologation_num = fields.Char(string='Vehicle FIA homologation num')
    x_vehicle_number_plate = fields.Char(string='Vehicle number plate')
    chassis_no = fields.Char(string="Chassis")
    # nomination
    x_race_info_pit_id = fields.Char(string='Pit ID')
    x_nomination_year = fields.Char(string='Nomination Year')
    x_date_enrolement_reveived = fields.Date(string='Date Enrolement Received')
    x_nomination_status = fields.Char(string='Nomination Status')
    x_race_info_field = fields.Many2one('rennfelder', string='Race field')
    x_race_info_starting_num = fields.Char(string='Starting Number')
    x_pit_box_number = fields.Integer(string='Pit Box Number')
    x_vehicle_inspection_passed = fields.Char(string='Vehicle inspection passed?')
    x_autorized = fields.Char(string='Autorized to start?')
    website_published = fields.Boolean(default=True)
    image_url_vehical = fields.Char(string="URL")
    type = fields.Selection(
        [('contact', 'Contact'),
         ('invoice', 'Invoice address'),
         ('delivery', 'Shipping address'),
         ('other', 'Relative Address'),
         ("private", "Private Address"),
        ], string='Address Type',
        default='contact',
        help="Used by Sales and Purchase Apps tx_nom_confirmedo select the relevant address depending on the context.")

    state = fields.Selection([('draft','Draft'),('registered','Registered'),('confirmed','Confirmed'),('rejected','Rejected'),('attended','Attended')], compute="_compute_state", string="Registeration State", store=True)
    #x_nom_registered = fields.Boolean(string="Registered for Nomination", help="Registered for nomination")
    x_nom_registered_dat = fields.Datetime(compute="_compute_x_nom_dat", string="Registered for nomination date", help="Registered for nomination date", store=True)
    #x_nom_confirmed = fields.Boolean(string="Nomination confirmed", help="Nomination confirmed")
    x_nom_confirmed_dat = fields.Datetime(compute="_compute_x_nom_dat", string="Nomination confirmed date", help="Nomination confirmed date", store=True)
    #x_nom_rejected = fields.Boolean(string="Nomination rejected", help="Nomination rejected")
    x_nom_rejected_dat = fields.Datetime(compute="_compute_x_nom_dat", string="Nomination rejected date", help="Nomination rejected date", store=True)
    x_nom_waitlist = fields.Boolean(string="Nomination waitlist", help="Nomination waitlist")
    x_nom_waitlist_dat = fields.Datetime(compute="_compute_x_nom_dat", string="Nomination waitlist date", help="Nomination waitlist date", store=True)
    x_doc_approval = fields.Boolean(string="Document approval", help="Document approval")
    x_doc_approval_dat = fields.Datetime(compute="_compute_x_nom_dat", string="Document approval date", help="Document approval date", store=True)
    x_tech_approval = fields.Boolean(string="Technical approval", help="Technical approval")
    x_tech_approval_dat = fields.Datetime(compute="_compute_x_nom_dat", string="Technical approval date", help="Technical approval date", store=True)
    x_nom_qualified = fields.Boolean(string="Qualified", help="Qualified")
    x_nom_qualified_dat = fields.Datetime(compute="_compute_x_nom_dat", string="Qualified date", help="Qualified date", store=True)

    event_registration_ids = fields.One2many('event.registration', 'partner_id', string="Event Registration")

    @api.model
    def set_website_pulished_true(self):
        partner_ids = self.env['res.partner'].sudo().search([])
        partner_ids.write({'website_published': True})


class VehicleCode(models.Model):
    _name = "vehicle.code"

    name = fields.Char(string='Name', required=True, translate=True)


class Rennfelder(models.Model):
    _name = "rennfelder"
    _description = "Renn felder"
    _order = 'sequence'

    name = fields.Char(string='Name', required=True, translate=True)
    sequence = fields.Integer(help='Used to order Journals in the dashboard view', default=10)
    note = fields.Html("Note")


class DriverLicenseCodes(models.Model):
    _name = "driver.license.codes"

    name = fields.Char(string='Name', required=True, translate=True)


class ShirtSizeCodes(models.Model):
    _name = "shirt.size.codes"

    name = fields.Char(string='Name', required=True, translate=True)
