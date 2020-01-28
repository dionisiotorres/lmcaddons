# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ResPartner(models.Model):
    _inherit = "res.partner"
    _description = 'Contact'

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
    x_race_info_starting_num = fields.Integer(string='Starting Number')
    x_pit_box_number = fields.Integer(string='Pit Box Number')
    x_vehicle_inspection_passed = fields.Char(string='Vehicle inspection passed?')
    x_autorized = fields.Char(string='Autorized to start?')
    website_published = fields.Boolean(default=True)
    type = fields.Selection(
        [('contact', 'Contact'),
         ('invoice', 'Invoice address'),
         ('delivery', 'Shipping address'),
         ('other', 'Relative Address'),
         ("private", "Private Address"),
        ], string='Address Type',
        default='contact',
        help="Used by Sales and Purchase Apps to select the relevant address depending on the context.")

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
    note = fields.Text("Note")


class DriverLicenseCodes(models.Model):
    _name = "driver.license.codes"

    name = fields.Char(string='Name', required=True, translate=True)


class ShirtSizeCodes(models.Model):
    _name = "shirt.size.codes"

    name = fields.Char(string='Name', required=True, translate=True)
