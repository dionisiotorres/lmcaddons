# -*- coding: utf-8 -*-

import base64
import logging
import psycopg2
import smtplib
import re
from odoo import _, api, exceptions, fields, models
from datetime import datetime, timedelta
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
from odoo.tools import pycompat
from odoo import tools

_logger = logging.getLogger(__name__)


class MessageTag(models.Model):
    _name = "message.tag"

    name = fields.Char(string='Tag Name')


class MessageFolder(models.Model):
    _name = "message.folder"

    name = fields.Char(string='Folder Name')


class Message(models.Model):
    _inherit = 'mail.message'

    msg_unread = fields.Boolean('Message Read')
    message_label = fields.Selection([('inbox','Inbox'), ('starred', 'Starred'),('done', 'Done'), ('snoozed', 'Snoozed'), ('draft', 'Draft'), ('sent', 'SENT'), ('trash', 'TRASH')], string='Message Label', default="inbox")
    draft_message_id = fields.Char(string='Draft Message ID')
    snoozed_time = fields.Datetime('Snoozed Time')
    partner_followers = fields.Many2many('res.partner', 'mail_message_partner_rel', 'mail_id', 'partner_id', string='Partners')
    tag_ids = fields.Many2many('message.tag', 'mail_message_tags_rel', 'mail_id', 'tag_id', string='Tag')
    folder_id = fields.Many2one('message.folder', string='Folder')
    email_cc_ids = fields.Many2many('res.partner', 'mail_notification_cc', 'message_id', 'partner_id', string='CC',
        help='Partners that have a notification pushing this message in their mailboxes')
    email_bcc_ids = fields.Many2many('res.partner', 'mail_notification_bcc', 'message_id', 'partner_id', string='BCC',
        help='Partners that have a notification pushing this message in their mailboxes')
    fetchmail_server_id = fields.Many2one('fetchmail.server', "Inbound Mail Server", readonly=True, index=True)

    @api.model
    def create(self, values):
        rec = super(Message, self).create(values)

        fetchmail_server_id = self.env.context.get('fetchmail_server_id')
        if fetchmail_server_id:
            fetchmail_server = self.env['fetchmail.server'].browse(int(fetchmail_server_id))
            folder_id = self.env['message.folder'].search([('name', '=', fetchmail_server.name)])
            if not folder_id:
                folder_id = self.env['message.folder'].create({'name': fetchmail_server.name})
            values['folder_id'] = folder_id.id
            values['fetchmail_server_id'] = fetchmail_server_id

        # tasks = self.env['project.task'].search([('id', '=', rec.res_id)])
        # if tasks:
        #     partners = tasks.message_follower_ids.mapped('partner_id.id')
        #     rec.partner_followers = [(6, 0, partners)]
        return rec

    @api.multi
    def write(self, values):
        fetchmail_server_id = self.env.context.get('fetchmail_server_id')
        if fetchmail_server_id:
            fetchmail_server = self.env['fetchmail.server'].browse(int(fetchmail_server_id))
            folder_id = self.env['message.folder'].search([('name', '=', fetchmail_server.name)])
            if not folder_id:
                folder_id = self.env['message.folder'].create({'name': fetchmail_server.name})
            values['folder_id'] = folder_id.id
            values['fetchmail_server_id'] = fetchmail_server_id
        return super(Message, self).write(values)


    def get_messages_time(self, your_time=None):
        if your_time == 'tomorrow':
            snooze = fields.Datetime.context_timestamp(self, datetime.now() + timedelta(days=1)).strftime("%a %I:%M %p")
        else:
            snooze = fields.Datetime.context_timestamp(self, datetime.now() + timedelta(hours=2)).strftime("%I:%M %p")
        return snooze

    @api.model
    def set_to_inbox(self):
        domain = [('message_label', '=', 'snoozed')]
        all_message = self.sudo().search(domain)
        for msg in all_message:
            now = fields.Datetime.from_string(fields.Datetime.now())
            snoozed_time = fields.Datetime.from_string(msg.snoozed_time)
            if snoozed_time and snoozed_time <= now:
                msg.message_label = 'inbox'

    @api.model
    def message_fetch(self, domain, limit=20):
        domain += [('message_type', '!=', 'email')]
        return self.search(domain, limit=limit).message_format()


class Partner(models.Model):
    _inherit = "res.partner"

    @api.model
    def get_needaction_count(self):
        """ compute the number of needaction of the current user """
        if self.env.user.partner_id:
            self.env.cr.execute("""
                SELECT count(*) as needaction_count
                FROM mail_message_res_partner_needaction_rel R
                LEFT JOIN mail_message msg ON (msg.id=R.mail_message_id)
                WHERE R.res_partner_id = %s AND (R.is_read = false OR R.is_read IS NULL) AND msg.message_type != 'email'""", (self.env.user.partner_id.id,))
            return self.env.cr.dictfetchall()[0].get('needaction_count')
        _logger.error('Call to needaction_count without partner_id')
        return 0

    @api.model
    def _notify_prepare_email_values(self, message):
        mail_values = super(Partner, self)._notify_prepare_email_values(message)
        cc_email_list = message.email_cc_ids.mapped('email')
        bcc_email_list = message.email_bcc_ids.mapped('email')
        cc_bcc = {
            'email_cc': ",".join(cc_email_list),
            'email_bcc': ",".join(bcc_email_list),
        }
        mail_values.update(cc_bcc)
        return mail_values


class MailMail(models.Model):
    _inherit = 'mail.mail'

    email_bcc = fields.Char(string='Bcc', help='Black Carbon copy message recipients')

    @api.multi
    def _send(self, auto_commit=False, raise_exception=False, smtp_session=None):
        IrMailServer = self.env['ir.mail_server']
        IrAttachment = self.env['ir.attachment']
        for mail_id in self.ids:
            success_pids = []
            failure_type = None
            processing_pid = None
            mail = None
            try:
                mail = self.browse(mail_id)
                if mail.state != 'outgoing':
                    if mail.state != 'exception' and mail.auto_delete:
                        mail.sudo().unlink()
                    continue

                # remove attachments if user send the link with the access_token
                body = mail.body_html or ''
                attachments = mail.attachment_ids
                for link in re.findall(r'/web/(?:content|image)/([0-9]+)', body):
                    attachments = attachments - IrAttachment.browse(int(link))

                # load attachment binary data with a separate read(), as prefetching all
                # `datas` (binary field) could bloat the browse cache, triggerring
                # soft/hard mem limits with temporary data.
                attachments = [(a['datas_fname'], base64.b64decode(a['datas']), a['mimetype'])
                               for a in attachments.sudo().read(['datas_fname', 'datas', 'mimetype'])]

                # specific behavior to customize the send email for notified partners
                email_list = []
                if mail.email_to:
                    email_list.append(mail._send_prepare_values())
                for partner in mail.recipient_ids:
                    values = mail._send_prepare_values(partner=partner)
                    values['partner_id'] = partner
                    email_list.append(values)

                # headers
                headers = {}
                ICP = self.env['ir.config_parameter'].sudo()
                bounce_alias = ICP.get_param("mail.bounce.alias")
                catchall_domain = ICP.get_param("mail.catchall.domain")
                if bounce_alias and catchall_domain:
                    if mail.model and mail.res_id:
                        headers['Return-Path'] = '%s+%d-%s-%d@%s' % (bounce_alias, mail.id, mail.model, mail.res_id, catchall_domain)
                    else:
                        headers['Return-Path'] = '%s+%d@%s' % (bounce_alias, mail.id, catchall_domain)
                if mail.headers:
                    try:
                        headers.update(safe_eval(mail.headers))
                    except Exception:
                        pass

                # Writing on the mail object may fail (e.g. lock on user) which
                # would trigger a rollback *after* actually sending the email.
                # To avoid sending twice the same email, provoke the failure earlier
                mail.write({
                    'state': 'exception',
                    'failure_reason': _('Error without exception. Probably due do sending an email without computed recipients.'),
                })
                # Update notification in a transient exception state to avoid concurrent
                # update in case an email bounces while sending all emails related to current
                # mail record.
                notifs = self.env['mail.notification'].search([
                    ('is_email', '=', True),
                    ('mail_id', 'in', mail.ids),
                    ('email_status', 'not in', ('sent', 'canceled'))
                ])
                if notifs:
                    notif_msg = _('Error without exception. Probably due do concurrent access update of notification records. Please see with an administrator.')
                    notifs.sudo().write({
                        'email_status': 'exception',
                        'failure_type': 'UNKNOWN',
                        'failure_reason': notif_msg,
                    })

                # build an RFC2822 email.message.Message object and send it without queuing
                res = None
                for email in email_list:
                    msg = IrMailServer.build_email(
                        email_from=mail.email_from,
                        email_to=email.get('email_to'),
                        subject=mail.subject,
                        body=email.get('body'),
                        body_alternative=email.get('body_alternative'),
                        email_cc=tools.email_split(mail.email_cc),
                        email_bcc=tools.email_split(mail.email_bcc),
                        reply_to=mail.reply_to,
                        attachments=attachments,
                        message_id=mail.message_id,
                        references=mail.references,
                        object_id=mail.res_id and ('%s-%s' % (mail.res_id, mail.model)),
                        subtype='html',
                        subtype_alternative='plain',
                        headers=headers)
                    processing_pid = email.pop("partner_id", None)
                    try:
                        res = IrMailServer.send_email(
                            msg, mail_server_id=mail.mail_server_id.id, smtp_session=smtp_session)
                        if processing_pid:
                            success_pids.append(processing_pid)
                        processing_pid = None
                    except AssertionError as error:
                        if str(error) == IrMailServer.NO_VALID_RECIPIENT:
                            failure_type = "RECIPIENT"
                            # No valid recipient found for this particular
                            # mail item -> ignore error to avoid blocking
                            # delivery to next recipients, if any. If this is
                            # the only recipient, the mail will show as failed.
                            _logger.info("Ignoring invalid recipients for mail.mail %s: %s",
                                         mail.message_id, email.get('email_to'))
                        else:
                            raise
                if res:  # mail has been sent at least once, no major exception occured
                    mail.write({'state': 'sent', 'message_id': res, 'failure_reason': False})
                    _logger.info('Mail with ID %r and Message-Id %r successfully sent', mail.id, mail.message_id)
                    # /!\ can't use mail.state here, as mail.refresh() will cause an error
                    # see revid:odo@openerp.com-20120622152536-42b2s28lvdv3odyr in 6.1
                mail._postprocess_sent_message(success_pids=success_pids, failure_type=failure_type)
            except MemoryError:
                # prevent catching transient MemoryErrors, bubble up to notify user or abort cron job
                # instead of marking the mail as failed
                _logger.exception(
                    'MemoryError while processing mail with ID %r and Msg-Id %r. Consider raising the --limit-memory-hard startup option',
                    mail.id, mail.message_id)
                # mail status will stay on ongoing since transaction will be rollback
                raise
            except (psycopg2.Error, smtplib.SMTPServerDisconnected):
                # If an error with the database or SMTP session occurs, chances are that the cursor
                # or SMTP session are unusable, causing further errors when trying to save the state.
                _logger.exception(
                    'Exception while processing mail with ID %r and Msg-Id %r.',
                    mail.id, mail.message_id)
                raise
            except Exception as e:
                failure_reason = tools.ustr(e)
                _logger.exception('failed sending mail (id: %s) due to %s', mail.id, failure_reason)
                mail.write({'state': 'exception', 'failure_reason': failure_reason})
                mail._postprocess_sent_message(success_pids=success_pids, failure_reason=failure_reason, failure_type='UNKNOWN')
                if raise_exception:
                    if isinstance(e, (AssertionError, UnicodeEncodeError)):
                        if isinstance(e, UnicodeEncodeError):
                            value = "Invalid text: %s" % e.object
                        else:
                            # get the args of the original error, wrap into a value and throw a MailDeliveryException
                            # that is an except_orm, with name and value as arguments
                            value = '. '.join(e.args)
                        raise MailDeliveryException(_("Mail Delivery Failed"), value)
                    raise

            if auto_commit is True:
                self._cr.commit()
        return True

class MailThread(models.AbstractModel):
    _inherit = 'mail.thread'

    @api.multi
    @api.returns('mail.message', lambda value: value.id)
    def message_post(self, body='', subject=None,
                     message_type='notification', subtype=None,
                     parent_id=False, attachments=None,
                     notif_layout=False, add_sign=True, model_description=False,
                     mail_auto_delete=True, **kwargs):
        """ Post a new message in an existing thread, returning the new
            mail.message ID.
            :param int thread_id: thread ID to post into, or list with one ID;
                if False/0, mail.message model will also be set as False
            :param str body: body of the message, usually raw HTML that will
                be sanitized
            :param str type: see mail_message.message_type field
            :param int parent_id: handle reply to a previous message by adding the
                parent partners to the message in case of private discussion
            :param tuple(str,str) attachments or list id: list of attachment tuples in the form
                ``(name,content)``, where content is NOT base64 encoded
            Extra keyword arguments will be used as default column values for the
            new mail.message record. Special cases:
                - attachment_ids: supposed not attached to any document; attach them
                    to the related document. Should only be set by Chatter.
            :return int: ID of newly created mail.message
        """
        if attachments is None:
            attachments = {}
        if self.ids and not self.ensure_one():
            raise exceptions.Warning(_('Invalid record set: should be called as model (without records) or on single-record recordset'))

        # if we're processing a message directly coming from the gateway, the destination model was
        # set in the context.
        model = False
        if self.ids:
            self.ensure_one()
            model = kwargs.get('model', False) if self._name == 'mail.thread' else self._name
            if model and model != self._name and hasattr(self.env[model], 'message_post'):
                return self.env[model].browse(self.ids).message_post(
                    body=body, subject=subject, message_type=message_type,
                    subtype=subtype, parent_id=parent_id, attachments=attachments,
                    notif_layout=notif_layout, add_sign=add_sign,
                    mail_auto_delete=mail_auto_delete, model_description=model_description, **kwargs)

        # 0: Find the message's author, because we need it for private discussion
        author_id = kwargs.get('author_id')
        if author_id is None:  # keep False values
            author_id = self.env['mail.message']._get_default_author().id

        # 2: Private message: add recipients (recipients and author of parent message) - current author
        #   + legacy-code management (! we manage only 4 and 6 commands)
        partner_ids = set()
        kwargs_partner_ids = kwargs.pop('partner_ids', [])
        for partner_id in kwargs_partner_ids:
            if isinstance(partner_id, (list, tuple)) and partner_id[0] == 4 and len(partner_id) == 2:
                partner_ids.add(partner_id[1])
            if isinstance(partner_id, (list, tuple)) and partner_id[0] == 6 and len(partner_id) == 3:
                partner_ids |= set(partner_id[2])
            elif isinstance(partner_id, pycompat.integer_types):
                partner_ids.add(partner_id)
            else:
                pass  # we do not manage anything else
        if parent_id and not model:
            parent_message = self.env['mail.message'].browse(parent_id)
            private_followers = set([partner.id for partner in parent_message.partner_ids])
            if parent_message.author_id:
                private_followers.add(parent_message.author_id.id)
            private_followers -= set([author_id])
            partner_ids |= private_followers

        # 4: mail.message.subtype
        subtype_id = kwargs.get('subtype_id', False)
        if not subtype_id:
            subtype = subtype or 'mt_note'
            if '.' not in subtype:
                subtype = 'mail.%s' % subtype
            subtype_id = self.env['ir.model.data'].xmlid_to_res_id(subtype)

        # automatically subscribe recipients if asked to
        if self._context.get('mail_post_autofollow') and self.ids and partner_ids:
            partner_to_subscribe = partner_ids
            if self._context.get('mail_post_autofollow_partner_ids'):
                partner_to_subscribe = [p for p in partner_ids if p in self._context.get('mail_post_autofollow_partner_ids')]
            self.message_subscribe(list(partner_to_subscribe))

        # _mail_flat_thread: automatically set free messages to the first posted message
        MailMessage = self.env['mail.message']
        if self._mail_flat_thread and model and not parent_id and self.ids:
            messages = MailMessage.search(['&', ('res_id', '=', self.ids[0]), ('model', '=', model)], order="id ASC", limit=1)
            parent_id = messages.ids and messages.ids[0] or False
        # we want to set a parent: force to set the parent_id to the oldest ancestor, to avoid having more than 1 level of thread
        elif parent_id:
            messages = MailMessage.sudo().search([('id', '=', parent_id), ('parent_id', '!=', False)], limit=1)
            # avoid loops when finding ancestors
            processed_list = []
            if messages:
                message = messages[0]
                while (message.parent_id and message.parent_id.id not in processed_list):
                    processed_list.append(message.parent_id.id)
                    message = message.parent_id
                parent_id = message.id
        # import pdb;pdb.set_trace()
        values = kwargs
        values.update({
            'author_id': author_id,
            'model': model,
            'res_id': model and self.ids[0] or False,
            'body': body,
            'subject': subject or False,
            'message_type': message_type,
            'parent_id': parent_id,
            'subtype_id': subtype_id,
            'partner_ids': [(4, pid) for pid in partner_ids],
            'channel_ids': kwargs.get('channel_ids', []),
            'add_sign': add_sign,
            'email_cc_ids':[(6,0, kwargs.get('email_cc_ids'))] if kwargs.get('email_cc_ids') else False,
            'email_bcc_ids':[(6,0, kwargs.get('email_bcc_ids'))] if kwargs.get('email_bcc_ids') else False,
        })
        if notif_layout:
            values['layout'] = notif_layout

        # 3. Attachments
        #   - HACK TDE FIXME: Chatter: attachments linked to the document (not done JS-side), load the message
        attachment_ids = self._message_post_process_attachments(attachments, kwargs.pop('attachment_ids', []), values)
        values['attachment_ids'] = attachment_ids

        # Avoid warnings about non-existing fields
        for x in ('from', 'to', 'cc'):
            values.pop(x, None)

        # Post the message
        # canned_response_ids are added by js to be used by other computations (odoobot)
        # we need to pop it from values since it is not stored on mail.message
        canned_response_ids = values.pop('canned_response_ids', False)
        new_message = MailMessage.create(values)
        values['canned_response_ids'] = canned_response_ids
        self._message_post_after_hook(new_message, values, model_description=model_description, mail_auto_delete=mail_auto_delete)
        return new_message