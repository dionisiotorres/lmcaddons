# -*- coding: utf-8 -*-

import binascii
import logging
import os

from odoo import http

# Imports the Google Cloud client library
from google.cloud import vision
from google.cloud.vision import types

_logger = logging.getLogger(__name__)
current_dir = os.path.dirname(__file__)


class VisionAPI(http.Controller):
    @http.route('/check/vision', type='json', auth="public", methods=['POST'], website=True, csrf=False)
    def check_vision(self, **post):
        if not post.get('fileContents'):
            return {'success': False}

        credential = os.path.join(current_dir, 'DAG-cda728af956d.json')
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = credential

        # Instantiates a client
        client = vision.ImageAnnotatorClient()

        # Names of likelihood from google.cloud.vision.enums
        likelihood_name = (
            'UNKNOWN', 'VERY_UNLIKELY', 'UNLIKELY', 'POSSIBLE', 'LIKELY', 'VERY_LIKELY')

        base64_content = post.get('fileContents')
        base64_content = base64_content.replace('data:image/jpeg;base64,', '')
        base64_content = base64_content.replace('data:image/png;base64,', '')
        content = binascii.a2b_base64(base64_content)

        image = types.Image(content=content)

        # Performs label detection on the image file
        response = client.label_detection(image=image)
        ress_datas = []
        res_faces_datas = []
        res_lm_datas = []
        res_logos_datas = []
        res_anno_datas =[]
        labels = response.label_annotations

        response_faces = client.face_detection(image=image)
        faces = response_faces.face_annotations

        response_landmark = client.face_detection(image=image)
        landmarks = response_landmark.landmark_annotations

        response_logo = client.face_detection(image=image)
        logos = response_logo.logo_annotations

        annotations = response.web_detection

        if labels:
            ress_datas.append('LABELS:')
            print('LABELS:')
            for label in labels:
                ress_datas.append(label.description)
                print(label.description)

        if faces:
            res_faces_datas.append('FACES:')
            print('FACES:')
            for face in faces:
                print('anger: {}'.format(likelihood_name[face.anger_likelihood]))
                print('joy: {}'.format(likelihood_name[face.joy_likelihood]))
                print('surprise: {}'.format(likelihood_name[face.surprise_likelihood]))
                res_faces_datas.append('Anger: {}'.format(likelihood_name[face.anger_likelihood]))
                res_faces_datas.append('Joy: {}'.format(likelihood_name[face.joy_likelihood]))
                res_faces_datas.append('Surprise: {}'.format(likelihood_name[face.surprise_likelihood]))

                vertices = (['({},{})'.format(vertex.x, vertex.y)
                    for vertex in face.bounding_poly.vertices])
                print('face bounds: {}'.format(','.join(vertices)))
                res_faces_datas.append('face bounds: {}'.format(','.join(vertices)))

        if landmarks:
            print('LANDMARKS:')
            res_lm_datas.append('LANDMARKS:')
            for landmark in landmarks:
                print(landmark.description)
                for location in landmark.locations:
                    lat_lng = location.lat_lng
                    print('Latitude {}'.format(lat_lng.latitude))
                    print('Longitude {}'.format(lat_lng.longitude))
                    res_lm_datas.append('Latitude {}'.format(lat_lng.latitude))
                    res_lm_datas.append('Longitude {}'.format(lat_lng.longitude))

        if logos:
            print('LOGOS:')
            res_logos_datas.append('LOGOS:')
            for logo in logos:
                print(logo.description)
                res_logos_datas.append(logo.description)

        if annotations:
            if annotations.best_guess_labels:
                print('ANNOTATIONS:')
                res_anno_datas.append('ANNOTATIONS:')
                for label in annotations.best_guess_labels:
                    print('\nBest guess label: {}'.format(label.label))
                    res_anno_datas.append('Best guess label: {}'.format(label.label))

            if annotations.pages_with_matching_images:
                print('\n{} Pages with matching images found:'.format(
                    len(annotations.pages_with_matching_images)))

                for page in annotations.pages_with_matching_images:
                    print('\n\tPage url   : {}'.format(page.url))

                    if page.full_matching_images:
                        print('\t{} Full Matches found: '.format(
                            len(page.full_matching_images)))

                        for image in page.full_matching_images:
                            print('\t\tImage url  : {}'.format(image.url))

                    if page.partial_matching_images:
                        print('\t{} Partial Matches found: '.format(
                            len(page.partial_matching_images)))

                        for image in page.partial_matching_images:
                            print('\t\tImage url  : {}'.format(image.url))

            if annotations.web_entities:
                print('\n{} Web entities found: '.format(
                    len(annotations.web_entities)))

                for entity in annotations.web_entities:
                    print('\n\tScore      : {}'.format(entity.score))
                    print(u'\tDescription: {}'.format(entity.description))

            if annotations.visually_similar_images:
                print('\n{} visually similar images found:\n'.format(
                    len(annotations.visually_similar_images)))

                for image in annotations.visually_similar_images:
                    print('\tImage url    : {}'.format(image.url))

        # print("res_datas__________", ress_datas)
        return {'success': True, 'datass': ress_datas, 'faces_datas': res_faces_datas, 'lm_datas' : res_lm_datas, 'logos_datas': res_logos_datas, 'anno_datas': res_anno_datas}

