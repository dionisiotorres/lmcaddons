# -*- coding: utf-8 -*-
#################################################################################
# Author      : Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# Copyright(c): 2015-Present Webkul Software Pvt. Ltd.
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
{
  "name"                 :  "Odoo Website Advertisement Manager",
  "summary"              :  "The module allows the Odoo user to host advertisements on his Odoo Website. The user can sell the website space to display advertisements of other companies, etc.",
  "category"             :  "Website",
  "version"              :  "1.0.0",
  "sequence"             :  0,
  "author"               :  "Webkul Software Pvt. Ltd.",
  "license"              :  "Other proprietary",
  "website"              :  "https://store.webkul.com/Odoo-Website-Advertisement-Manager.html",
  "description"          :  """Odoo Website Advertisement Manager
Host advertisements on Odoo website
Display advertisements on website
Rent website space for advertisements""",
  "live_test_url"        :  "http://odoodemo.webkul.com/?module=website_advertisement_manager&lout=0&custom_url=/advertisement",
  "depends"              :  [
                             'website_sale',
                             'sale_management',
                            ],
  "data"                 :  [
                             'security/access_control_security.xml',
                             'security/ir.model.access.csv',
                             'edi/mail_to_customer_on_content_approval.xml',
                             'data/ad_block_data.xml',
                             'views/templates.xml',
                             'views/res_config_settings_views.xml',
                             'views/website_ad_block.xml',
                             'views/website_ad_order.xml',
                             'views/website_block_sol_views.xml',
                             'views/inherit_website_templates.xml',
                             'views/inherit_website_cart_templates.xml',
                             'views/website_ad_templates.xml',
                             'views/my_account_ad_blocks_template.xml',
                             'views/kanak_templates.xml',
                            ],
  "demo"                 :  ['demo/ad_block_demo_data.xml'],
  "images"               :  ['static/description/Banner.png'],
  "application"          :  True,
  "installable"          :  True,
  "auto_install"         :  False,
  "price"                :  99,
  "currency"             :  "EUR",
  "pre_init_hook"        :  "pre_init_check",
}