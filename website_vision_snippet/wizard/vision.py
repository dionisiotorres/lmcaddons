# -*- coding: utf-8 -*-

from odoo import models, api, fields
import base64
import os 


class GoogleVision(models.TransientModel):
    _name = 'google.vision'
    
    images = fields.Binary(string='images')

    def add_file(self):
        file = os.path.dirname(__file__)
        file = file.replace('wizard', 'static/src')
        with open(file + '/credentials.json', 'wb') as f:
            data = base64.b64decode(self.images)
            f.write(data)
        

        
    
   

