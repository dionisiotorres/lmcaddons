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

from odoo import api, fields, models
from datetime import date, datetime
import logging
_logger = logging.getLogger(__name__)

class WebsiteAdOrder(models.Model):
    _name = "website.ad.order"
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
    _rec_name = "name"
    _order = "id desc"
    _description = "Advertisement Order"

    @api.depends('line_ids.price_subtotal')
    def _compute_total_amount(self):
        for rec in self:
            total_amount = 0.0
            total_blocks = 0
            for line in rec.line_ids:
                total_amount += line.price_subtotal
                total_blocks += 1
            rec.update({
                'total_amount': rec.currency_id.round(total_amount),
                'total_blocks': total_blocks,
            })

    name = fields.Char("Name", required=True, copy=False, readonly=True, default="New", track_visibility='onchange')
    partner_id = fields.Many2one("res.partner", "Customer", track_visibility='onchange', required=True)
    total_amount = fields.Monetary("Total", track_visibility='onchange', readonly= True,
        compute="_compute_total_amount")
    total_blocks = fields.Integer("Total Blocks", readonly= True, compute="_compute_total_amount")
    currency_id = fields.Many2one("res.currency",
        string="Currency",
        required=True,
        default= lambda self: self.env.user.company_id.currency_id.id,
    )
    line_ids = fields.One2many("website.ad.order.lines",
        'ad_order_id',
        string="Ad Order Lines",
        copy= True,
    )
    note = fields.Text('Note')
    order_id = fields.Many2one("sale.order")

    @api.model
    def create(self,vals):
        vals['name'] = self.env['ir.sequence'].next_by_code("website.ad.order")
        res = super(WebsiteAdOrder, self).create(vals)
        return res

class WebsiteAdOrderLines(models.Model):
    _name = "website.ad.order.lines"
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
    _rec_name = "ad_block_id"
    _order = "id desc"
    _description = "Advertisement Order Lines"

    ad_order_id = fields.Many2one("website.ad.order", string="Ad Order")
    ad_block_id = fields.Many2one("website.ad.block", string="Block Position", required=True)
    date_from = fields.Date(string="Date From", required=True, default=fields.Date.today(), track_visibility='onchange')
    date_to = fields.Date(string="Date To", required=True, default=fields.Date.today(), track_visibility='onchange')
    total_days = fields.Integer("Number Of Days", readonly=True, compute="_compute_total_days")
    price_unit = fields.Monetary(string="Price per Day",
        related= "ad_block_id.price",
        store= True,
        track_visibility= 'onchange',
        required= True,
    )
    currency_id = fields.Many2one("res.currency", related="ad_order_id.currency_id")
    price_subtotal = fields.Monetary(string="Price Subtotal", compute="_compute_subtotal")
    status = fields.Selection([
        ("draft", "Draft"),
        ("active", "Active"),
        ("expire", "Expire"),
    ], string="Status", default="draft", track_visibility='onchange')
    display_type = fields.Selection([
        ("banner", "Banner"),
        # ("products", "Products"),
    ], string="Display Type", default="banner", required=True)
    banner_img = fields.Binary("Banner Image")
    banner_link = fields.Char("Banner Link")
    product_ids = fields.Many2many("product.template", "ad_order_id", "product_tmplate_id", "ad")

    @api.depends("total_days")
    def _compute_subtotal(self):
        for rec in self:
            if rec.total_days:
                rec.price_subtotal = rec.price_unit * rec.total_days
        return

    @api.depends("date_from", "date_to")
    def _compute_total_days(self):
        for rec in self:
            if rec.date_from and rec.date_to:
                d0 = datetime.strptime(rec.date_from,"%Y-%m-%d").date()
                d1 = datetime.strptime(rec.date_to,"%Y-%m-%d").date()
                diff = d1 - d0
                rec.total_days = diff.days
        return
