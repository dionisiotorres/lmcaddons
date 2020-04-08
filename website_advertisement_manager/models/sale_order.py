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

from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import date,datetime,timedelta
from dateutil.relativedelta import relativedelta
import logging
_logger = logging.getLogger(__name__)

class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.depends('order_line')
    def _compute_total_ad_blocks(self):
        for rec in self:
            total_ad_blocks = 0
            for line in rec.order_line:
                total_ad_blocks += 1
            rec.update({
                'total_ad_blocks': total_ad_blocks,
            })

    total_ad_blocks = fields.Integer("Total Blocks", readonly= True, compute="_compute_total_ad_blocks")
    is_ad_block_order = fields.Boolean("Ad Block Order", help="Products added in this order will be for Advertisement Block")

    @api.onchange('order_line')
    def compute_ad_block_order(self):
        for rec in self:
            rec.is_ad_block_order = False
            if rec.order_line:
                if any((line.product_id.is_ad_block) for line in rec.order_line):
                    rec.is_ad_block_order = True

    @api.multi
    def _website_product_id_change(self, order_id, product_id, qty=0):
        res = super(SaleOrder, self)._website_product_id_change(order_id, product_id, qty)
        product = self.env['product.product'].browse(product_id)
        if product and product.is_ad_block:
            ad_vals = self._context.get("ad_vals")
            if ad_vals:
                ad_date_from = ad_vals.get("ad_date_from")
                ad_date_to = ad_vals.get("ad_date_to")
                vals = {
                    'is_ad_block_line': True,
                    'ad_date_to': ad_date_to,
                    'ad_date_from': ad_date_from,
                }
                res.update(vals)
                order = self.env['sale.order'].browse(order_id)
                order.is_ad_block_order = True
        return res

    @api.multi
    @api.depends('website_order_line.product_uom_qty', 'website_order_line.product_id')
    def _compute_cart_info(self):
        res = super(SaleOrder, self)._compute_cart_info()
        for order in self:
            prod_lines = order.website_order_line.filtered(lambda l: l.is_ad_block_line==False)
            ad_lines = order.website_order_line.filtered(lambda l: l.is_ad_block_line)
            cart_quantity = int(sum(prod_lines.mapped('product_uom_qty'))) + len(ad_lines)
            order.cart_quantity = cart_quantity
        return res

    @api.multi
    def action_confirm(self):
        res = super(SaleOrder, self).action_confirm()
        for rec in self:
            if rec.is_ad_block_order:
                if rec.order_line:
                    for line in rec.order_line:
                        vals = {
                            "product_id": line.product_id.id,
                        }
                        line._check_block_dates_availability(vals)
        return res

    @api.multi
    def action_draft(self):
        res = super(SaleOrder, self).action_draft()
        for rec in self:
            if rec.is_ad_block_order and rec.order_line:
                ad_line = rec.order_line.filtered(lambda l: l.is_ad_block_line == True)
                if ad_line:
                    for line in rec.order_line:
                        line.ad_block_status = 'draft'
                        line.ad_content_status = 'new'
        return res

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'
    _order = 'ad_block_status'

    ad_date_from = fields.Date(string="Date From", required=True, default=fields.Date.today())
    ad_date_to = fields.Date(string="Date To", required=True, default=fields.Date.today())
    ad_total_days = fields.Integer("Number Of Days", readonly=True, compute="_compute_total_ad_days")
    ad_block_status = fields.Selection([
        ("draft", "Draft"),
        ("active", "Active"),
        ("expire", "Expired"),
    ], string="Status", default="draft", compute="_compute_ad_block_status", search="_search_ad_block_status")
    ad_content_status = fields.Selection([
        ("new", "New"),
        ("pending", "Pending"),
        ("approved", "Approved"),
        ("denied", "Denied"),
    ], string="Ad Content Status", default="new")
    note = fields.Text("Note")
    ad_display_type = fields.Selection([
        ("banner", "Banner"),
    ], string="Ad Display Type", default="banner", required=True)
    ad_banner_img = fields.Binary("Banner Image")
    ad_banner_link = fields.Char("Banner Link")
    is_ad_block_line = fields.Boolean("Ad Block Order Line",
        compute="_compute_ad_block_line",
        store=True,
        help="Product of this order line will be of Advertisement Block")
    ad_img_name = fields.Text("Ad Image Name")
    ad_block_product_tmpl_id = fields.Many2one("product.template","Ad Product Template", related="product_id.product_tmpl_id")
    color = fields.Integer("Color")

    @api.multi
    def _search_ad_block_status(self, operator, value):
        line_ids = []
        if operator == '!=':
            for obj in self.sudo().search([]):
                if obj.ad_block_status != value:
                    line_ids.append(obj.id)
        if operator == '=':
            for obj in self.sudo().search([]):
                if obj.ad_block_status == value:
                    line_ids.append(obj.id)
        return [('id', 'in', line_ids)]

    @api.multi
    def _compute_ad_block_status(self):
        for rec in self:
            rec.ad_block_status = 'draft'
            date_today = date.today()
            ad_expire_day = datetime.strptime(str(rec.ad_date_to),"%Y-%m-%d").date() + timedelta(days=1)
            ad_date_from = datetime.strptime(str(rec.ad_date_from),"%Y-%m-%d").date()
            ad_date_to = datetime.strptime(str(rec.ad_date_to),"%Y-%m-%d").date()
            if rec.is_ad_block_line and rec.state == 'sale':
                if date_today >= ad_expire_day:
                    rec.ad_block_status = 'expire'
                if date_today == ad_date_from or date_today == ad_date_to:
                    rec.ad_block_status = 'active'
            if rec.is_ad_block_line and rec.state == 'cancel':
                if date_today >= ad_expire_day:
                    rec.ad_block_status = 'expire'
                if date_today == ad_date_from or date_today == ad_date_to:
                    rec.ad_block_status = 'draft'
        return

    @api.multi
    @api.onchange('ad_banner_img', 'ad_banner_link')
    def _update_ad_content_status(self):
        for rec in self:
            rec.ad_content_status = 'new'
        return

    @api.depends("ad_date_from", "ad_date_to")
    def _compute_total_ad_days(self):
        for rec in self:
            if rec.ad_date_from and rec.ad_date_to:
                d0 = datetime.strptime(str(rec.ad_date_from),"%Y-%m-%d").date()
                d1 = datetime.strptime(str(rec.ad_date_to),"%Y-%m-%d").date()
                diff = d1 - d0
                rec.ad_total_days = diff.days + 1
                rec.product_uom_qty = diff.days + 1
        return

    @api.depends('product_id')
    def _compute_ad_block_line(self):
        for rec in self:
            rec.is_ad_block_line = False
            if rec.product_id and rec.product_id.is_ad_block:
                rec.is_ad_block_line = True

    @api.model
    def create(self, vals):
        res = super(SaleOrderLine, self).create(vals)
        res._check_block_dates_availability(vals)
        return res

    def _get_date_list(self, date_from, date_to):
        date_list = []
        date_from = datetime.strptime(str(date_from),"%Y-%m-%d").date()
        date_to = datetime.strptime(str(date_to),"%Y-%m-%d").date()
        delta = date_to - date_from
        for i in range(delta.days + 1):
            date_list.append(date_from + timedelta(days=i))
        return date_list

    def _validate_ad_date(self, checkdate):
        d1 = datetime.strptime(str(checkdate),"%Y-%m-%d").date()
        d2 = date.today()
        rd = relativedelta(d2,d1)
        if rd.days > 0 or rd.months > 0 or rd.years > 0:
            raise UserError(_("Date Should be after Today"))

    def _check_block_dates_availability(self, vals):
        product_id = vals.get("product_id") if vals.get("product_id") else self.product_id
        if type(product_id)==int:
            product_id = self.env['product.product'].browse(product_id)
        if product_id and product_id.is_ad_block:

            # check for date should be after today
            if self.ad_date_from:
                self._validate_ad_date(self.ad_date_from)
            if self.ad_date_to:
                self._validate_ad_date(self.ad_date_to)

            # check for date from must be less than date to
            if self.ad_date_from and self.ad_date_to:
                if datetime.strptime(str(self.ad_date_to),"%Y-%m-%d").date() < datetime.strptime(str(self.ad_date_from),"%Y-%m-%d").date():
                    raise UserError(_("Selected Date From must be less than selected Date To"))

            # list of all dates of this block
            order_lines = self.env['sale.order.line'].search([('product_id','=', product_id.id),
                ('id','!=',self.id),('is_ad_block_line','=',True),('state','=','sale')])
            block_date_list = []
            for line in order_lines:
                block_date_list += self._get_date_list(line.ad_date_from, line.ad_date_to)
            block_date_list = list(set(block_date_list))

            # list of dates of current line block
            curr_date_list = self._get_date_list(self.ad_date_from, self.ad_date_to) or []

            # check for duplicates
            if block_date_list and curr_date_list:
                if any( date in block_date_list for date in curr_date_list):
                    raise UserError(_("This slot time is not available for this block."))
        return

    @api.multi
    def write(self, vals):
        res = super(SaleOrderLine, self).write(vals)
        if vals.get('ad_date_from') or vals.get("ad_date_to"):
            self._check_block_dates_availability(vals)
        return res

    def _compute_portal_url(self):
        super(SaleOrderLine, self)._compute_portal_url()
        for line in self:
            line.portal_url = '/my/ad/blocks/%s' % (line.id)

    def send_ad_block_status_update_mail(self):
        if self.env['ir.default'].sudo().get('res.config.settings', 'auto_approve_ad_block'):
            template_id = self.sudo().env.ref("website_advertisement_manager.content_approval_template_to_customer")
            template_id.send_mail(self.id,force_send=True)
        return True

    @api.multi
    def ad_content_approve(self):
        for rec in self:
            rec.write({"ad_content_status": "approved"})
            rec.send_ad_block_status_update_mail()
        return True

    @api.multi
    def ad_content_auto_approve(self):
        for rec in self:
            ad_block_auto_approve = self.env['ir.default'].sudo().get('res.config.settings', 'auto_approve_ad_block')
            if ad_block_auto_approve:
                rec.write({"ad_content_status": "pending"})
                rec.ad_content_approve()
            else:
                rec.write({"ad_content_status": "pending"})
        return True

    @api.multi
    def ad_content_set_pending(self):
        for rec in self:
            rec.ad_content_auto_approve()

    @api.multi
    def ad_content_deny(self):
        for rec in self:
            rec.write({"ad_content_status": "denied"})
        return True

    @api.multi
    def ad_content_set_new(self):
        for rec in self:
            rec.write({"ad_content_status": "new"})
        return True
