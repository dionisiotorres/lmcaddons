# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import models, fields, api


class EventRegistration(models.Model):

    _inherit = 'event.registration'

    open_ended_answer_ids = fields.One2many(
        'event.answer.open', inverse_name='registration_id', string='Answers'
    )


class EventQuestion(models.Model):

    _inherit = 'event.question'

    open_ended = fields.Boolean(help='Mark if this question is open ended.')

    open_ended_answer_ids = fields.One2many(
        'event.answer.open', inverse_name='question_id', string='Answers'
    )

    @api.multi
    def write(self, vals):
        """Wipe event.answer if question is open ended"""
        if vals.get('open_ended'):
            vals['answer_ids'] = [(5, False, False)]
        return super().write(vals)

    @api.model
    def create(self, vals):
        """Ensure no event.answer is created if question is open ended"""
        if vals.get('open_ended') and vals.get('answer_ids'):
            vals.pop('answer_ids')
        return super().create(vals)


class EventAnswerOpen(models.Model):

    _name = 'event.answer.open'
    _description = 'Answers to open ended questions'
    _order = 'question_sequence'

    question_sequence = fields.Integer(
        related='question_id.sequence', store=True
    )
    question_id = fields.Many2one(
        'event.question', required=True, ondelete='cascade'
    )
    registration_id = fields.Many2one(
        'event.registration', required=True, ondelete='cascade'
    )
    answer = fields.Text()
