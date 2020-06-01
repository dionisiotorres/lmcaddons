# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo.addons.website_event_questions.controllers.main import WebsiteEvent


class WebsiteEventController(WebsiteEvent):

    def _process_registration_details(self, details):
        ''' Process data posted from the attendee details form. '''
        # No direct call to super here to ensure website_event_questions'
        # controller is not skipped through inheritance
        question_controller = WebsiteEvent()
        registrations = question_controller._process_registration_details(
            details)
        for registration in registrations:
            open_answers = []
            for key, value in registration.items():
                if key.startswith('open-answers-'):
                    open_answers.append([0, 0, {
                        'question_id': key.split('open-answers-')[-1],
                        'answer': value,
                    }])
            registration['open_ended_answer_ids'] = open_answers
        return registrations
