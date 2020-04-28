# -*- coding: utf-8 -*-
import base64
import werkzeug
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

from odoo import http, fields
from odoo.http import request
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT


class WebsiteOdooInbox(http.Controller):

    _message_per_page = 50

    def _render_odoo_message(self, domain=[], link='/mail', page=1, label=None, color='#4285F4', search=None, existing_tag=None, existing_folder=None):
        if not label:
            label = 'inbox'
        if label == 'inbox':
            domain += [('folder_id', '=', False)]

        MailMessage = request.env['mail.message'].sudo()
        all_message = MailMessage.search(domain)

        today_messages = []
        yesterday_messages = []
        thismonth_messages = []
        more_messages = []
        user_id = request.env.user
        # domain += [('model', '!=', False)]
        counter_domain = []
        # if label == 'sent':
        #     partner_id = request.env.user.partner_id
        if user_id:
            partner_id = request.env.user.partner_id
            if partner_id:
                if label != 'sent':
                    domain += ['|', '|', ('partner_ids', 'in', partner_id.ids), ('needaction_partner_ids', 'in', partner_id.ids), ('starred_partner_ids', 'in', partner_id.ids)]
                counter_domain = ['|', '|', ('partner_ids', 'in', partner_id.ids), ('needaction_partner_ids', 'in', partner_id.ids), ('starred_partner_ids', 'in', partner_id.ids)]

        mails = MailMessage.search(domain, offset=(page-1)*self._message_per_page, limit=self._message_per_page, order="date desc")
        for msg in mails:
            # import pdb;pdb.set_trace()
            if fields.Date.to_string(msg.date) == datetime.today().date() or any(fields.Date.to_string(i.date) == datetime.today().date() for i in msg.child_ids):
                today_messages.append({'parent_id': msg, 'child_ids': sorted(msg.child_ids, key=lambda r: r.date, reverse=True)})
            elif fields.Date.to_string(msg.date) == (datetime.today().date() - relativedelta(days=1)) or any(fields.Date.to_string(i.date) == datetime.today().date() for i in msg.child_ids):
                yesterday_messages.append({'parent_id': msg, 'child_ids': sorted(msg.child_ids, key=lambda r: r.date, reverse=True)})
            elif fields.Date.from_string(msg.date).month == datetime.today().month or any(fields.Date.to_string(i.date) == datetime.today().date() for i in msg.child_ids):
                thismonth_messages.append({'parent_id': msg, 'child_ids': sorted(msg.child_ids, key=lambda r: r.date, reverse=True)})
            else:
                more_messages.append({'parent_id': msg, 'child_ids': sorted(msg.child_ids, key=lambda r: r.date, reverse=True)})

        tag_ids = request.env['message.tag'].sudo().search([])
        folder_ids = request.env['message.folder'].sudo().search([])

        count_parent_messages = MailMessage.search(counter_domain)
        # count_parent_messages = count_mails.filtered(lambda self: not self.parent_id)

        inbox_mssg_count = count_parent_messages.filtered(lambda e: e.msg_unread == False and e.message_label in ['inbox','starred'] and not e.folder_id)
        starred_mssg_count = count_parent_messages.filtered(lambda e: e.msg_unread == False and e.message_label == 'starred')
        snoozed_mssg_count = count_parent_messages.filtered(lambda e: e.msg_unread == False and e.message_label == 'snoozed')
        folder_mssg_count = count_parent_messages.filtered(lambda e: e.msg_unread == False and e.folder_id.id == existing_folder)
        counter_fd_msgs = {}
        for fid in folder_ids.ids:
            ct = len(count_parent_messages.filtered(lambda e: e.msg_unread == False and e.folder_id.id == fid))
            counter_fd_msgs.update({str(fid): str(ct)})

        total = 0
        if label == 'inbox':
            total = len(count_parent_messages.filtered(lambda e: e.message_label in ['inbox', 'starred'] and not e.folder_id))
        elif label == 'starred':
            total = len(count_parent_messages.filtered(lambda e: e.message_label == 'starred'))
        elif label == 'snoozed':
            total = len(count_parent_messages.filtered(lambda e: e.message_label == 'snoozed'))
        elif existing_folder:
            total = len(count_parent_messages.filtered(lambda e: e.folder_id.id == existing_folder))

        pager = request.website.pager(
            url=link,
            total=total,
            page=page,
            step=self._message_per_page,
        )
        return request.render('odoo_inbox.inbox', {
            'today_messages': today_messages,
            'yesterday_messages': yesterday_messages,
            'thismonth_messages': thismonth_messages,
            'more_messages': more_messages,
            'pager': pager,
            'needaction': len(all_message.filtered('needaction')),
            'total': total,
            'current': (page)*self._message_per_page,
            'previouse': (page-1)*self._message_per_page,
            'starred': label == 'starred' and True or False,
            'done': label == 'done' and True or False,
            'snooze': label == 'snoozed' and True or False,
            'draft': label == 'draft' and True or False,
            'sent': label == 'sent' and True or False,
            'trash': label == 'trash' and True or False,
            'label': label,
            'color': color,
            'search': search,
            'tag_ids': tag_ids,
            'existing_tag': existing_tag,
            'folder_ids': folder_ids,
            'existing_folder': existing_folder,
            'inbox_mssg_count': len(inbox_mssg_count),
            'starred_mssg_count': len(starred_mssg_count),
            'snoozed_mssg_count': len(snoozed_mssg_count),
            'folder_mssg_count' : len(folder_mssg_count),
            'counter_fd_msgs': counter_fd_msgs,
        })

    @http.route(['/mail/message_read'], type='json', auth="public", website=True)
    def odoo_message_read(self, **kw):
        message = request.env['mail.message'].browse(kw.get('message'))
        for m in message:
            for n in m.notification_ids:
                if n.res_partner_id == request.env.user.partner_id:
                    m.msg_unread = True
        domain = []
        MailMessage = request.env['mail.message'].sudo()
        user_id = request.env.user
        if user_id:
            partner_id = request.env.user.partner_id
            if partner_id:
                domain = ['|', '|', ('partner_ids', 'in', partner_id.ids), ('needaction_partner_ids', 'in', partner_id.ids), ('starred_partner_ids', 'in', partner_id.ids)]
        parent_messages = MailMessage.search(domain)
        # parent_messages = mails.filtered(lambda self: not self.parent_id)
        inbox_mssg_count = parent_messages.filtered(lambda e: e.msg_unread == False and e.message_label in ['inbox','starred'] and not e.folder_id)
        starred_mssg_count = parent_messages.filtered(lambda e: e.msg_unread == False and e.message_label == 'starred')
        snoozed_mssg_count = parent_messages.filtered(lambda e: e.msg_unread == False and e.message_label == 'snoozed')
        folder_mssg_count = parent_messages.filtered(lambda e: e.msg_unread == False and e.folder_id)
        folder_ids = request.env['message.folder'].sudo().search([])
        counter_fd_msgs = {}
        for fid in folder_ids.ids:
            ct = len(parent_messages.filtered(lambda e: e.msg_unread == False and e.folder_id.id == fid))
            counter_fd_msgs.update({str(fid): str(ct)})

        return {'msg_unread': True, 'inbox_mssg_count': len(inbox_mssg_count), 'starred_mssg_count': len(starred_mssg_count), 'snoozed_mssg_count':len(snoozed_mssg_count), 'folder_mssg_count': len(folder_mssg_count), 'counter_fd_msgs': counter_fd_msgs}

    @http.route(['/mail/all_mssg_unread'], type='json', auth="public", website=True)
    def odoo_all_message_unread(self, messg_ids, **kw):
        for mssg in messg_ids:
            message = request.env['mail.message'].sudo().browse(int(mssg))
            message.msg_unread = False
        return True

    @http.route(['/mail/all_mssg_read'], type='json', auth="public", website=True)
    def odoo_all_message_read(self, messg_ids, **kw):
        for mssg in messg_ids:
            message = request.env['mail.message'].sudo().browse(int(mssg))
            message.msg_unread = True
        return True

    @http.route(['/mail/inbox',
                 '/mail/inbox/page/<int:page>',
                 '/mail/search_message'
                 ], type='http', auth="public", website=True)
    def odoo_inbox(self, page=1, **kw):
        search = None
        if kw.get('search'):
            domain = ['|', '|', '|',
                      ('subject', 'ilike', kw.get('search')),
                      ('email_from', 'ilike', kw.get('search')),
                      ('body', 'ilike', kw.get('search')),
                      ('tag_ids.name', 'ilike', kw.get('search'))]
            search = kw.get('search')
        else:
            domain = [('message_label', 'in', ['starred', 'inbox'])]
        return self._render_odoo_message(domain, '/mail/inbox', page, 'inbox', search=search)

    @http.route(['/mail/message_post'], type='http', auth="public", website=True)
    def message_post_send(self, **post):
        subject = post.get('subject')
        body = post.get('body')
        messageObj = request.env['mail.message'].browse(int(post.get('message_id')))
        if messageObj.author_id:
            partner = messageObj.author_id
            files = request.httprequest.files.getlist('attachments')
            attachment_ids = []
            if files:
                for i in files:
                    if i.filename != '':
                        attachments = {
                                'name': i.filename,
                                'res_name': i.filename,
                                'res_model': 'res.partner',
                                'res_id': partner.id,
                                'datas': base64.encodestring(i.read()),
                                'datas_fname': i.filename,
                            }
                        attachment = request.env['ir.attachment'].sudo().create(attachments)
                        attachment_ids.append(attachment.id)

            message = partner.message_post(
                    body=body,
                    subject=subject,
                    model='res.partner',
                    res_id=partner.id,
                    email_from='%s <%s>' % (request.env.user.name, request.env.user.email),
                    author_id=request.env.user.partner_id.id,
                    parent_id=messageObj.id,
                    subtype_id=messageObj.subtype_id.id,
                    attachment_ids=attachment_ids,
                    partner_ids=[partner.id],
                    message_type=messageObj.message_type,
                )

            message.msg_unread = False
        return request.redirect('/mail/inbox')

    @http.route(['/sent_mail/mail'], type='http', auth="public", website=True)
    def mail_send(self, **post):
        if post:
            partners = request.httprequest.form.getlist('partners')
            # if partners:
            #     post['partners_list'] = map(int, partners)
            cc_partners = request.httprequest.form.getlist('cc_partners')
            # if cc_partners:
            #     post['cc_partners_list'] = map(int, cc_partners)
            bcc_partners = request.httprequest.form.getlist('bcc_partners')
            # if bcc_partners:
            #     post['bcc_partners_list'] = map(int, bcc_partners)

            # import pdb;pdb.set_trace()
            subject = post.get('subject')
            body = post.get('body')
            partner_ids = email_cc_ids = email_bcc_ids = False
            if partners:
                partner_ids = request.env['res.partner'].browse(map(int, partners))
            if cc_partners:
                email_cc_ids = request.env['res.partner'].browse(map(int, cc_partners))
            if bcc_partners:
                email_bcc_ids = request.env['res.partner'].browse(map(int, bcc_partners))
            # for partner in request.env['res.partner'].browse(map(int, partners)):
            attachment_ids = []
            files = request.httprequest.files.getlist('compose_attachments')
            if files:
                for i in files:
                    if i.filename != '':
                        attachments = {
                                'name': i.filename,
                                'res_name': i.filename,
                                'res_model': 'res.partner',
                                # 'res_id': partner.id,
                                'datas': base64.encodestring(i.read()),
                                'datas_fname': i.filename,
                            }
                        attachment = request.env['ir.attachment'].sudo().create(attachments)
                        attachment_ids.append(attachment.id)

            message = request.env['res.partner'].message_post(
                body=body,
                subject=subject,
                model='res.partner',
                # res_id=partner.id,
                email_from='%s <%s>' % (request.env.user.name, request.env.user.email),
                author_id=request.env.user.partner_id.id,
                attachment_ids=attachment_ids,
                partner_ids=partner_ids.ids,
                email_cc_ids=email_cc_ids.ids if email_cc_ids else False,
                email_bcc_ids=email_bcc_ids.ids if email_bcc_ids else False,
                message_type='email',
            )
            message.msg_unread = False
        return request.redirect('/mail/inbox')

    @http.route(['/mail/send/<model("mail.message"):message>',
                 ], type='http', auth="public", website=True)
    def odoo_move_send(self, message=None, **post):
        message = request.env['odoo.inbox'].move_to_send(message)
        return request.redirect('/mail/send')

    @http.route(['/mail/send',
                 '/mail/send/page/<int:page>'
                 ], type='http', auth="public", website=True)
    def odoo_send(self, page=1, **kw):
        domain = [('author_id', '=', request.env.user.partner_id.id), ('message_type', '=', 'email')]
        return self._render_odoo_message(domain, '/mail/send', page, 'sent', '#898984')

    @http.route(['/mail/starred/message',
                 ], type='json', auth="public", website=True)
    def message_starred(self, **kw):
        message = request.env['mail.message'].browse(kw.get('message'))
        if kw.get('action') == 'add':
            message.starred_partner_ids = [(4, request.env.user.partner_id.id)]
            request.env['odoo.inbox'].set_star(kw.get('action'), message)
        if kw.get('action') == 'remove':
            message.starred_partner_ids = [(2, request.env.user.partner_id.id)]
            request.env['odoo.inbox'].set_star(kw.get('action'), message)

    @http.route('/mail/all_mssg_starred', type="json", auth="public", website=True)
    def odoo_all_mssg_starred(self, messg_ids, **kw):
        for mssg in messg_ids:
            message = request.env['mail.message'].sudo().browse(int(mssg))
            if kw.get('action') == 'add':
                message.starred_partner_ids = [(4, request.env.user.partner_id.id)]
                request.env['odoo.inbox'].set_star(kw.get('action'), message)
        return True

    @http.route('/mail/all_mssg_unstarred', type="json", auth="public", website=True)
    def odoo_all_mssg_unstarred(self, messg_ids, **kw):
        for mssg in messg_ids:
            message = request.env['mail.message'].sudo().browse(int(mssg))
            if kw.get('action') == 'remove':
                message.starred_partner_ids = [(2, request.env.user.partner_id.id)]
                request.env['odoo.inbox'].set_star(kw.get('action'), message)
        return True

    @http.route(['/mail/starred',
                 '/mail/starred/page/<int:page>'
                 ], type='http', auth="public", website=True)
    def odoo_starred(self, page=1, **kw):
        domain = [('message_label', '=', 'starred')]
        return self._render_odoo_message(domain, '/mail/starred', page, 'starred', '#f9bd3d')

    @http.route(['/mail/starred_move_to_inbox/<model("mail.message"):message>',
                 ], type='http', auth="public", website=True)
    def starred_move_to_inbox(self, message=None, **kw):
        message.message_label = 'inbox'
        return request.redirect('/mail/starred')

    @http.route(['/mail/snoozed',
                 '/mail/done/page/<int:page>'
                 ], type='http', auth="public", website=True)
    def odoo_snoozed(self, page=1, **kw):
        domain = [('message_label', '=', 'snoozed')]
        return self._render_odoo_message(domain, '/mail/snoozed', page, 'snoozed', '#ef6c00')

    @http.route(['/mail/snoozed/<model("mail.message"):message>',
                 ], type='http', auth="public", website=True)
    def set_snoozed(self, message=None, your_time=None, **post):
        message.message_label = 'snoozed'
        your_time = str(your_time)
        if your_time == 'today':
            message.snoozed_time = datetime.now() + timedelta(hours=2)
        elif your_time == 'tomorrow':
            message.snoozed_time = datetime.now() + timedelta(days=1)
        elif your_time == 'nexweek':
            message.snoozed_time = datetime.now() + timedelta(days=7)
        if post.get('date'):
            message.snoozed_time = datetime.strptime(str(post.get('date')), "%m/%d/%Y %I:%M %p").strftime(DEFAULT_SERVER_DATETIME_FORMAT)
        return request.redirect('/mail/inbox')


    @http.route(['/mail/all_mssg_snoozed',
                 ], type='json', auth="public", website=True)
    def all_set_snoozed(self, mssg_snooze=None, your_time=None, **post):
        for mssg in mssg_snooze:
            message_id = request.env['mail.message'].sudo().browse(int(mssg))
            message_id.message_label = 'snoozed'
            if your_time == 'today':
                message_id.snoozed_time = datetime.now() + timedelta(hours=2)
            elif your_time == 'tomorrow':
                message_id.snoozed_time = datetime.now() + timedelta(days=1)
            elif your_time == 'nexweek':
                message_id.snoozed_time = datetime.now() + timedelta(days=7)
            # if snooze_date:
            #     message_id.snoozed_time = datetime.strptime(snooze_date, "%m/%d/%Y %I:%M %p").strftime(DEFAULT_SERVER_DATETIME_FORMAT)
        return True


    @http.route(['/mail/all_mssg_snoozed_submit',
                 ], type='json', auth="public", website=True)
    def all_set_snoozed_submit(self, mssg_snooze=None, snooze_date=None, **post):
        for mssg in mssg_snooze:
            message_id = request.env['mail.message'].sudo().browse(int(mssg))
            message_id.message_label = 'snoozed'
            if snooze_date:
                message_id.snoozed_time = datetime.strptime(snooze_date, "%m/%d/%Y %I:%M %p").strftime(DEFAULT_SERVER_DATETIME_FORMAT)
        return True

    @http.route(['/mail/set_done/<model("mail.message"):message>',
                 ], type='http', auth="public", website=True)
    def message_done(self, message=None, **kw):
        request.env['odoo.inbox'].set_done(message)
        return request.redirect('/mail/inbox')

    @http.route(['/mail/done',
                 '/mail/done/page/<int:page>'
                 ], type='http', auth="public", website=True)
    def mail_done(self, page=1, **kw):
        domain = [('message_label', '=', 'done')]
        return self._render_odoo_message(domain, '/mail/done', page, 'done', '#0f9d58')

    @http.route(['/mail/move_to_inbox/<model("mail.message"):message>',
                 ], type='http', auth="public", website=True)
    def move_to_inbox(self, message=None, **kw):
        message.message_label = 'inbox'
        return request.redirect('/mail/inbox')

    @http.route([
        '/mail/move_to_trash/<model("mail.message"):message>',
    ], type='http', auth="public", website=True)
    def odoo_move_trash(self, message=None, **post):
        message = request.env['odoo.inbox'].move_to_trash(message)
        return request.redirect('/mail/inbox')

    @http.route(['/mail/trash',
                 '/mail/trash/page/<int:page>'
                 ], type='http', auth="public", website=True)
    def odoo_trash(self, page=1, **kw):
        domain = [('message_label', '=', 'trash')]
        return self._render_odoo_message(domain, '/mail/trash', page, 'trash', '#898984')

    @http.route('/mail/all_mssg_trash', type="json", auth="public", website=True)
    def odoo_all_mssg_trash(self, messg_ids, **post):
        for mssg in messg_ids:
            message_id = request.env['mail.message'].sudo().browse(int(mssg))
            if message_id or message_id.folder_id:
                message_id.write({'folder_id': False,
                                  'message_label': 'trash'
                                  })
        return True

    @http.route('/mail/all_mssg_done', type="json", auth="public", website=True)
    def odoo_all_mssg_done(self, messg_ids, **post):
        for mssg in messg_ids:
            message_id = request.env['mail.message'].sudo().browse(int(mssg))
            if message_id or message_id.folder_id:
                message_id.write({'message_label': 'done'
                                  })
        return True


    @http.route('/mail/attachment/<model("ir.attachment"):attachment>/download', type='http', website=True)
    def slide_download(self, attachment):
        filecontent = base64.b64decode(attachment.datas)
        main_type, sub_type = attachment.mimetype.split('/', 1)
        disposition = 'attachment; filename=%s.%s' % (werkzeug.urls.url_quote(attachment.name), sub_type)
        return request.make_response(
            filecontent,
            [('Content-Type', attachment.mimetype),
             ('Content-Length', len(filecontent)),
             ('Content-Disposition', disposition)])
        return request.render("website.403")

    @http.route('/mail/partner_create', type="json", auth="public", website=True)
    def odoo_partner_create(self, email_address, **post):
        if email_address:
            # import pdb;pdb.set_trace()
            partner_id = request.env['res.partner'].sudo().search([('name', '=', email_address.split('@')[0]), ('email', '=', email_address)])
            if not partner_id:
                partner_id = request.env['res.partner'].sudo().create({
                    'name': email_address.split('@')[0],
                    'email': email_address
                    })
            return {'success': True, 'partner_id': partner_id.id, 'partner_name': partner_id.name, 'email': partner_id.email}
        else:
            return {'error': 'email address is wrong'}

    @http.route('/mail/message_tag_assign', type="json", auth="public", website=True)
    def odoo_message_tag_assign(self, message_id, tag_ids=[], create_tag_input=None, **post):
        if message_id:
            message = request.env['mail.message'].sudo().browse(message_id)
            if create_tag_input:
                new_tag_id = request.env['message.tag'].sudo().create({'name': create_tag_input})
                tag_ids += [new_tag_id.id]
            message.tag_ids = [(6, 0, tag_ids)]
            main_tag_ids = request.env['message.tag'].sudo().search([])
            message_tag_list_template = request.env.ref('odoo_inbox.message_tag_list').render({'mail_message': message})
            message_tag_dropdown = request.env.ref('odoo_inbox.tag_dropdown').render({'mail_message': message, 'tag_ids': main_tag_ids})
            return {'success': True, 'message_tag_list': message_tag_list_template, 'message_tag_dropdown': message_tag_dropdown}
        else:
            return {'error': 'Message is not find'}

    @http.route('/mail/message_tag_assign/all', type="json", auth="public", website=True)
    def odoo_message_tag_assign_all(self, message_id=[], tag_ids=[], create_tag_input=None, **post):
        if message_id:
            message_ids = request.env['mail.message'].sudo().browse(message_id)
            if create_tag_input:
                new_tag_id = request.env['message.tag'].sudo().create({'name': create_tag_input})
                tag_ids += [new_tag_id.id]
            for message in message_ids:
                tttag_ids = list(set(tag_ids + message.tag_ids.ids))
                message.tag_ids = [(6, 0, tttag_ids)]
            return True
        else:
            return {'error': 'Message is not find'}


    @http.route('/mail/message_tag_delete', type="json", auth="public", website=True)
    def odoo_message_tag_delete(self, message_id, tag_id, **post):
        if message_id and tag_id:
            message = request.env['mail.message'].sudo().browse(message_id)
            message.tag_ids = [(3, tag_id)]
            main_tag_ids = request.env['message.tag'].sudo().search([])
            message_tag_list_template = request.env.ref('odoo_inbox.message_tag_list').render({'mail_message': message})
            message_tag_dropdown = request.env.ref('odoo_inbox.tag_dropdown').render({'mail_message': message, 'tag_ids': main_tag_ids})
            return {'success': True, 'message_tag_list': message_tag_list_template, 'message_tag_dropdown': message_tag_dropdown}
        else:
            return {'error': 'Message is not find'}

    @http.route(['/mail/tag/<model("message.tag"):tag>'], type='http', auth="public", website=True)
    def odoo_tags(self, tag, **kw):
        domain = [('tag_ids', '=', tag.id)]
        page = 1
        return self._render_odoo_message(domain, '/mail/tag/' + str(tag.id), page, tag.name, '#51bcd4', existing_tag=tag.id)

    @http.route(['/mail/tag_edit'], type='http', auth="public", method=['POST'], website=True)
    def odoo_tags_edit(self, **kw):
        if kw.get('tag_id') and kw.get('tag_name'):
            tag_id = request.env['message.tag'].sudo().browse(int(kw.get('tag_id')))
            tag_id.name = kw.get('tag_name')
        return request.redirect(request.httprequest.referrer or '/mail/inbox')

    @http.route(['/mail/tag_delete'], type='http', auth="public", method=['POST'], website=True)
    def odoo_tags_delete(self, **kw):
        if kw.get('tag_id'):
            tag_id = request.env['message.tag'].sudo().browse(int(kw.get('tag_id')))
            tag_id.unlink()
        return request.redirect(request.httprequest.referrer or '/mail/inbox')

    @http.route(['/mail/folder/<model("message.folder"):folder>'], type='http', auth="public", website=True)
    def odoo_folders(self, folder, **kw):
        domain = [('folder_id', '=', folder.id)]
        page = 1
        return self._render_odoo_message(domain, '/mail/folder/' + str(folder.id), page, folder.name, '#4285F4', existing_folder=folder.id)

    @http.route(['/mail/folder_edit'], type='http', auth="public", method=['POST'], website=True)
    def odoo_folder_edit(self, **kw):
        if kw.get('folder_id') and kw.get('folder_name'):
            folder_id = request.env['message.folder'].sudo().browse(int(kw.get('folder_id')))
            folder_id.name = kw.get('folder_name')
        return request.redirect(request.httprequest.referrer or '/mail/inbox')

    @http.route(['/mail/folder_delete'], type='http', auth="public", method=['POST'], website=True)
    def odoo_folder_delete(self, **kw):
        if kw.get('folder_id'):
            folder_id = request.env['message.folder'].sudo().browse(int(kw.get('folder_id')))
            folder_id.unlink()
        return request.redirect('/mail/inbox')

    @http.route(['/mail/move_to_folder/<model("message.folder"):folder>/<model("mail.message"):message>'], type='http', auth="public", website=True)
    def odoo_move_to_folder(self, folder, message, **kw):
        if folder and message:
            message.folder_id = folder.id
        return request.redirect(request.httprequest.referrer or '/mail/inbox')

    @http.route('/mail/all_move_to_folder', type="json", auth="public", website=True)
    def odoo_all_move_to_folder(self, folder_id, messg_ids, **post):
        for mssg in messg_ids:
            message_id = request.env['mail.message'].sudo().browse(int(mssg))
            if folder_id == 'move_to_inbox':
                message_id.write({'folder_id': False, 'message_label': 'inbox',
                                  })
            elif folder_id and message_id:
                message_id.folder_id = folder_id
        return True


    @http.route(['/mail/folder/create'], type='http', auth="public", method="POST", website=True)
    def odoo_new_folder(self, **kw):
        if kw.get('create_folder'):
            folder_id = request.env['message.folder'].sudo().create({'name': kw.get('create_folder')})
            if kw.get('message_id') and folder_id:
                message_id = request.env['mail.message'].sudo().browse(int(kw.get('message_id')))
                message_id.folder_id = folder_id.id
        return request.redirect(request.httprequest.referrer or '/mail/inbox')
