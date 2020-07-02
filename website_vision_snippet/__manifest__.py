# -*- coding: utf-8 -*-
{
    'name': "Website Vision Snippet",
    'summary': """Face vision api""",
    'description': """""",
    'author': "Kanak Infosystems",
    'category': 'Website',
    'depends': ['website'],
    'data': [
        'wizard/vision_views.xml',
        'views/templates.xml',
        'views/google_vision_views.xml',
        
    ],
    'images': [
    ],
    'installable': True,
}

# Pre Install
# $ sudo pip3 install google-cloud
# $ sudo pip3 install google-cloud-vision
