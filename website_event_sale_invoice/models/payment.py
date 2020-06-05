# -*- coding: utf-8 -*-
from odoo import api, models


class PaymentTransaction(models.Model):
    _inherit = 'payment.transaction'

    def _transfer_form_validate(self, data):
        contextual_self = self.with_context(block_force_quotation_send=True)
        res = super(PaymentTransaction, contextual_self)._transfer_form_validate(data)
        self._invoice_event_sale_orders()
        default_template = self.env.ref('account.email_template_edi_invoice')
        if default_template:
            if self.invoice_ids:
                ctx_company = {
                    'company_id': self.acquirer_id.company_id.id,
                    'force_company': self.acquirer_id.company_id.id,
                    'mark_invoice_as_sent': True,
                }
                trans = self.with_context(ctx_company)
                for invoice in trans.invoice_ids:
                    invoice.message_post_with_template(int(default_template), notif_layout="mail.mail_notification_paynow")
        return res

    @api.multi
    def _invoice_event_sale_orders(self):
        for trans in self.filtered(lambda t: t.sale_order_ids):
            if any([order.order_line.mapped('event_id').filtered(lambda x: x.online_auto_invoice) for order in trans.sale_order_ids]):
                ctx_company = {
                    'company_id': trans.acquirer_id.company_id.id,
                    'force_company': trans.acquirer_id.company_id.id
                }
                trans = trans.with_context(**ctx_company)
                trans.sale_order_ids.action_confirm()
                trans.sale_order_ids._force_lines_to_event_invoice_policy_order()
                invoices = trans.sale_order_ids.action_invoice_create()
                trans.invoice_ids = [(6, 0, invoices)]
                invoices = trans.invoice_ids.filtered(lambda inv: inv.state == 'draft')
                if any([order.order_line.mapped('event_id').filtered(lambda x: x.auto_invoice_validate) for order in trans.sale_order_ids]):
                    invoices.action_invoice_open()
