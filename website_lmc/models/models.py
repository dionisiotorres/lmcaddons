# -*- coding: utf-8 -*-

from odoo import models, fields
from datetime import datetime


class Users(models.Model):
    _inherit = "res.users"

    def get_last_seen(self):
        time_now = datetime.now()
        last_seen = self.login_date

        time_delta_hours = (time_now - last_seen).total_seconds()
        time = round(time_delta_hours / 60)
        time_str = str(time) + ' minutes'
        if time > 59:
            time = round(time / 60)
            time_str = str(time) + ' hours'
            if time >= 24:
                time = round(time / 24)
                time_str = str(time) + ' days'
                if time >= 61:
                    time = round(time / 30)
                    time_str = str(time) + ' months'
                    if time >= 12:
                        time = round(time / 12)
                        time_str = str(time) + '+' + ' years'

        # hours = datetime.timedelta(hours=time_delta_minutes)
        return time_str


class Menu(models.Model):

    _inherit = "website.menu"
    is_show_menu = fields.Boolean("Is show menu", default=True)
