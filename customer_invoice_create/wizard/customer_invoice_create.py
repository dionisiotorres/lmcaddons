
from odoo import models, fields, api


class CustomerInvoiceCreate(models.TransientModel):
    _name = 'customer.invoice.create'

    date_invoice = fields.Date(string='Invoice Date')
    #payment_term_id = fields.Mnay2one('account.payment.term', string="Payment Term")
    product_ids = fields.Many2many('product.product', string='Product')

    @api.multi
    def create_invoice(self):
        #property_payment_term_id = False
        context = dict(self._context or {})
        invoice = self.env['account.invoice']
        invoice_line = self.env['account.invoice.line']
        partner_ids = self.env['res.partner'].browse(context.get('active_ids'))
        sale_journal = self.env['account.journal'].search([
            ('type', '=', 'sale')], limit=1)
        for record in self:
            for parnter in partner_ids:
                # if parnter.customer:
                #     property_payment_term_id = parnter.property_payment_term_id
                # if parnter.supplier:
                #     property_payment_term_id = parnter.property_supplier_payment_term_id
                invoices = invoice.create({
                    'partner_id': parnter.id,
                    'partner_shipping_id': parnter.id,
                    'date_invoice': record.date_invoice,
                    'type': 'out_invoice',
                    'journal_id': sale_journal.id,
                    #'payment_term_id': record.payment_term_id.id,
                    'account_id': parnter.property_account_receivable_id.id,
                })
                inv_line = None
                # Invoice Line Create
                for product in record.product_ids:
                    accounts = product.product_tmpl_id.get_product_accounts()
                    inv_line = invoice_line.create({
                        'name': product.name,
                        'invoice_id': invoices.id,
                        'product_id': product.id,
                        'account_id': accounts.get('income') and accounts['income'].id or False,
                        'price_unit': product.lst_price,
                        'quantity': 1,
                    })
                    inv_line._onchange_product_id()
