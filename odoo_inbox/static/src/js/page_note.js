odoo.define('odoo_inbox.page_note', function(require) {
    'use strict';

    require('web.dom_ready');
    var ajax = require('web.ajax');
    var core = require('web.core');
    var rpc = require('web.rpc');

    // var _t = core._t;
    // setInterval(page_refresh, 5 * 60000);
    // new gnMenu(document.getElementById('gn-menu'));
    // $('#compose_partner').select2();
    // $('#reply_partner').select2();

    var datepickers_options = {
        calendarWeeks: true,
        icons: {
            time: 'fa fa-clock-o',
            date: 'fa fa-calendar',
            up: 'fa fa-chevron-up',
            down: 'fa fa-chevron-down'
        },
    }

    $('.snooze_custome_time').datetimepicker(datepickers_options);

    $(document).ready(function() {
        $(".message__summary .message__summary__icon, .message__summary .message__summary__title, .message__summary .message__summary__body").click(function() {
            var $remove = $(this).closest('.message__summary');
            var message = $remove.data('message');
            $('#wrapper .message').removeClass("message--open").css('margin-top', '0%').css('margin-bottom', '0%');
            $(this).closest('.message').addClass("message--open");
            $(this).closest('.message').css('margin-top', '3%').css('margin-bottom', '3%');
            ajax.jsonRpc('/mail/message_read', 'call', {
                message: message,
            }).then(function(data) {
                data['msg_unread']
                $remove.removeClass('gmail_unread');
                $remove.addClass('gmail_read');
                if (data['inbox_mssg_count']){
                    $('.inbox_mssg_count').show();
                    $('.inbox_mssg_count').text(data['inbox_mssg_count']);
                }
                else{
                    $('.inbox_mssg_count').hide();
                }
                if (data['starred_mssg_count']){
                    $('.starred_mssg_count').show();
                    $('.starred_mssg_count').text(data['starred_mssg_count']);
                }
                else{
                    $('.starred_mssg_count').hide();
                }
                if (data['snoozed_mssg_count']){
                    $('.snoozed_mssg_count').show();
                    $('.snoozed_mssg_count').text(data['snoozed_mssg_count']);
                }
                else{
                    $('.snoozed_mssg_count').hide();
                }
                if(data['counter_fd_msgs']){
                    _.each(data['counter_fd_msgs'],function(val, index){
                        $("#counter_fd_msg" + index).text(val);
                        if(val == '0'){
                            $("#counter_fd_msg" + index).hide();
                        }else{
                            $("#counter_fd_msg" + index).show();
                        }
                    });
                }
                
                // if (data['folder_mssg_count']){
                //     $('.folder_mssg_count').show();
                //     $('.folder_mssg_count').text(data['folder_mssg_count']);
                // }
                // else{
                //     $('.folder_mssg_count').hide();
                // }
            });
        });

        $(".message__details__header").click(function() {
            var para = $('para')
            $(this).closest('.message').removeClass("message--open");
            $(this).closest('.message').css('margin-top', '0%').css('margin-bottom', '0%');
            $(this).parent().find('.message__details__footer_reply').hide()
            $(this).parent().find('.message__details__footer').show()
            $(this).parents().find('.reply_body_content .note-editable').html('').html(para)
            $(this).parents().find('#result').val('');

        });

        $('.right a.button-exit').click(function() {
            var para = $('para')
            $(this).parents().find('.min-hide input:text').val('');
            $(this).parents().find("#compose_partner").select2('val', false);
            $(this).parents().find('#header-newmail .note-editable').html('').html(para);
            $(this).parents("#newmail").find('#compose_attach_result').val('');
            $(this).parents("#newmail").find('#compose_attach_result').css('padding-top', '0px')
            $("#newmail").hide();
        });

        $('.list').click(function() {
            $('.head-menu .list').removeClass('active');
            $(this).addClass('active');
        });

        $('textarea.load_editor').each(function() {
            var $textarea = $(this);
            if (!$textarea.val().match(/\S/)) {
                $textarea.val("<p><br/></p>");
            }
            var $form = $textarea.closest('form');
            var toolbar = [
                ['style', ['style']],
                ['font', ['bold', 'italic', 'underline', 'clear']],
                ['para', ['ul', 'ol', 'paragraph']],
                ['table', ['table']],
                ['history', ['undo', 'redo']],
            ];
            $textarea.summernote({
                height: 275,
                toolbar: toolbar,
                styleWithSpan: false,
                placeholder: 'Say something'
            });

            $form.on('click', 'button, .a-submit', function() {
                $textarea.html($form.find('.note-editable').code());
            });
        });


        $.ajax({
            url: 'https://api.github.com/emojis',
            async: false
        }).then(function(data) {
            window.emojis = Object.keys(data);
            window.emojiUrls = data;
        });;

        // document.emojiType = 'unicode'; // default: image

        document.emojiSource = '/odoo_inbox/static/src/img/';

        $('textarea.load_editor1').each(function() {
            var $textarea = $(this);
            if (!$textarea.val().match(/\S/)) {
                $textarea.val("<p><br/></p>");
            }
            var $form = $textarea.closest('form');
            var toolbar = [
                ['style', ['style']],
                ['font', ['bold', 'italic', 'underline', 'clear']],
                ['para', ['ul', 'ol', 'paragraph']],
                ['table', ['table']],
                ['history', ['undo', 'redo']],
                // ['insert', ['emoji']],
                ['code', ['codeview']],
            ];
            $textarea.summernote({
                height: 120,
                toolbar: toolbar,
                styleWithSpan: false,
                focus: true,
                hint: {
                    match: /:([\-+\w]+)$/,
                    search: function(keyword, callback) {
                        callback($.grep(emojis, function(item) {
                            return item.indexOf(keyword) === 0;
                        }));
                    },
                    template: function(item) {
                        var content = emojiUrls[item];
                        return '<img src="' + content + '" width="20" /> :' + item + ':';
                    },
                    content: function(item) {
                        var url = emojiUrls[item];
                        if (url) {
                            return $('<img />').attr('src', url).css('width', 20)[0];
                        }
                        return '';
                    }
                },
                callbacks: {
                    onKeyup: function(event) {
                        setTimeout(function(){
                            var content = $(".load_editor1").val().replace(/<\/?[^>]+(>|$)/g, "");
                            var entered = content.split(' ').pop();
                            if (entered.length > 1 && entered.substring(0,1) == '@') {
                                var search = entered.substring(1, entered.length);
                                rpc.query({
                                    model: 'res.partner', method: 'get_mention_suggestions',
                                    args: [search, 5]
                                }).then(function (res) {
                                    var scontent = '';
                                    $.each(res[0], function (index, suggestion) {
                                        var tml = '<li class="o_mention_proposition" data-id="'+ suggestion.id +'"><span class="o_mention_name">' + suggestion.name + '</span><span class="o_mention_info">(' + suggestion.email + ')</span></li>';
                                        scontent += tml;
                                    });
                                    $('div.o_composer_mention_dropdown ul').html(scontent);
                                    $('div.o_composer_mention_dropdown').addClass('open');
                                    $('div.o_composer_mention_dropdown').attr('data-content', entered);

                                    $('div.o_composer_mention_dropdown li').click(function() {
                                        var user_id = $(this).attr('data-id');
                                        var username = $(this).find('.o_mention_name').text();
                                        var data_content = $('div.o_composer_mention_dropdown').attr('data-content');
                                        var upt_content = $(".load_editor1").val().replace(data_content, username);
                                        $('.load_editor1').summernote('code', upt_content);

                                        var $input_user_ids = $(this).parents('.reply_body_content').find('input[name=users_ids]');
                                        if ($input_user_ids.val()) {
                                            var updated_values = $input_user_ids.val() + ',' + user_id;
                                            $input_user_ids.val(updated_values);
                                        } else {
                                            $input_user_ids.val(user_id);
                                        }
                                        $('div.o_composer_mention_dropdown').removeClass('open');
                                    });
                                });
                            } else {
                                $('div.o_composer_mention_dropdown').removeClass('open');
                            }
                        },200);
                    }
                }
            });

            $form.on('click', 'button, .a-submit', function() {
                // $textarea.html($form.find('.note-editable').code());
            });
        });

        $('.message__details__footer .detail_mail_addrss span').click(function() {
            $(this).closest('.message__details__footer').hide();
            $(this).closest('.message__details__footer').next().show();
            var a = $(this).closest('.message__details').find('.message__details__body:last').find('.body_content').find('.body_mail_id_date').find('.date_content').find('span')[0].innerHTML;
            var b = $(this).closest('.message__details').find('.message__details__body:last').find('.body_content').find('.body_mail_id_date').find('.message__details__body_user_name')[0].innerHTML;
            var c = $(this).closest('.message__details').find('.message__details__body:last').find('.body_content').find('.message__details__body__content')[0].innerHTML;
            // var wrapper= document.createElement('div');
            // wrapper.append(a[0]);
            // wrapper.append(b[0]);
            var res = "<br/>" + "<br/>" + "<div><div dir='ltr'>" + "On " + a + " at " + b + " wrote:" + "<br/>" + "</div>" + "<blockquote style='margin:0px 0px 0px 0.8ex; padding-left:1ex'>" + "<div dir='ltr'>" + "<div>" + c + "</div>" + "</div>" + "</blockquote>" + "</div>"
            $(this).closest('.message__details__footer').next().find('.load_editor1').summernote('code', res);
        });

        $('.reply_delete_bttn').click(function() {
            var para = $('para')
            $(this).parents('.message__details__footer_reply').hide();
            $(this).parents('.message__details__footer_reply').prev().show();
            $(this).parents().find('.reply_body_content .note-editable').html('').html(para);
            $(this).parents(".message__details__footer_reply").find('#result').val('');
            // $(this).parents().find('.reply_body_content input[type=file]').val('');

        });


        $('.starred_btn i').on('click', function() {
            var message = $(this).parent().data('message');
            if ($(this).hasClass('fa fa-star-o')) {
                var action = 'add'
                $(this).removeClass('fa fa-star-o').addClass('fa fa-star');
            } else {
                var action = 'remove'
                $(this).removeClass('fa fa-star').addClass('fa fa-star-o');
            }
            ajax.jsonRpc('/mail/starred/message', 'call', {
                action: action,
                message: message
            }).then(function() {
                window.location.reload();
            });
        });

        $('.mark_as_done i').on('click', function() {
            $(this).css('color', 'green')
            var message = $(this).parent().data('message');
            var $remove = $(this)
            if (message) {
                return ajax.jsonRpc('/web/dataset/call_kw', 'call', {
                    model: 'mail.message',
                    method: 'set_message_done',
                    args: [message],
                    kwargs: {}
                });
                // .then(function(){
                //     console.log('ttttttttttttttttt')
                //     $remove.parents('.message__details__body').remove();
                //     // if ($remove.length === 1): {
                //     //     $remove.parents('.message').remove();
                //     // } else {
                //     //     $remove.parents('.message__details__body').remove();
                //     // }
                // });
            } else {
                return $.when();
            }
        });

        $(".arrow").click(function() {
            $(".collapse", $(this).parents('.msg-recipients')).toggle();
          });

        function validateEmail(email) {
            var re = /^(([^<>()[\]\\.,;:\s@"]+(\.[^<>()[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
            return re.test(email);
        }

        $('#compose_partner').select2({
            width: '100%',
            placeholder: "To",
            allowClear: true,
            createTag: function (params) {
               var value = params.term;
                if(validateEmail(value)) {
                    return {
                      id: value,
                      text: value,
                      newTag: true,
                    };
                }
                return null;
              },
        }).on('select2:select', function (evt) {
            if (evt.params.data.newTag){
                ajax.jsonRpc('/mail/partner_create', 'call', {
                    email_address: evt.params.data.text,
                }).then(function(data) {
                    $('#compose_partner option[value="'+evt.params.data.text+'"]').text(data.partner_name);
                    $('#compose_partner option[value="'+evt.params.data.text+'"]').text(data.email);
                    $('#compose_partner option[value="'+evt.params.data.text+'"]').attr('value', data.partner_id);
                });
            }
        });

        $('#cc_compose_partner').select2({
            width: '100%',
            placeholder: "Cc",
            allowClear: true,
            createTag: function (params) {
               var value = params.term;
                if(validateEmail(value)) {
                    return {
                      id: value,
                      text: value,
                      newTag: true,
                    };
                }
                return null;
              },
        }).on('select2:select', function (evt) {
            if (evt.params.data.newTag){
                ajax.jsonRpc('/mail/partner_create', 'call', {
                    email_address: evt.params.data.text,
                }).then(function(data) {
                    $('#cc_compose_partner option[value="'+evt.params.data.text+'"]').text(data.partner_name);
                    $('#cc_compose_partner option[value="'+evt.params.data.text+'"]').text(data.email);
                    $('#cc_compose_partner option[value="'+evt.params.data.text+'"]').attr('value', data.partner_id);
                });
            }
        });

        $('#bcc_compose_partner').select2({
            width: '100%',
            placeholder: "Bcc",
            allowClear: true,
            createTag: function (params) {
               var value = params.term;
                if(validateEmail(value)) {
                    return {
                      id: value,
                      text: value,
                      newTag: true,
                    };
                }
                return null;
              },
        }).on('select2:select', function (evt) {
            if (evt.params.data.newTag){
                ajax.jsonRpc('/mail/partner_create', 'call', {
                    email_address: evt.params.data.text,
                }).then(function(data) {
                    $('#bcc_compose_partner option[value="'+evt.params.data.text+'"]').text(data.partner_name);
                    $('#bcc_compose_partner option[value="'+evt.params.data.text+'"]').text(data.email);
                    $('#bcc_compose_partner option[value="'+evt.params.data.text+'"]').attr('value', data.partner_id);
                });
            }
        });

        function tags_dropdown_menu(){
            $('.tag-dropdown-menu, .label-container').click(function(e) {
                e.stopPropagation();
            });
            // $('.tag-dropdown-menu').find('input').change(function(e){
            //     $(this).closest('.tag-dropdown-menu').find('.apply_button').removeClass('hidden');
            // });
            $('.tag-dropdown-menu .apply_button a').click(function(e){
                var tag_ids = new Array();
                var this_val = $(this);
                var message_id = $(this).attr('data-message');
                var checked_box = $(this).closest('.tag_dropdown').find('input[type="checkbox"]:checked');
                $.each($(checked_box), function (key, value) {
                    tag_ids.push(parseInt($(value).val()));
                });
                var create_tag_input = $(this).closest('ul').find('.create_tag_input').val();
                if (message_id)
                {
                    if (!!create_tag_input)
                    {
                        create_tag_input = create_tag_input;
                    }
                    else
                    {
                        create_tag_input = false;
                    }
                    ajax.jsonRpc('/mail/message_tag_assign', 'call', {
                        message_id: parseInt(message_id),
                        tag_ids: tag_ids,
                        create_tag_input: create_tag_input,
                    }).then(function(data) {
                        if(!!data.message_tag_list){
                            this_val.closest('.message').find('.message_tag_list_details_body').html(data.message_tag_list);
                            this_val.closest('.message').find('.message_tag_dropdown_details').html(data.message_tag_dropdown);
                            this_val.closest('.tag_dropdown').removeClass('open');
                            remove_tag_function();
                            tags_dropdown_menu();
                        }
                    });
                }
            });
          }
        tags_dropdown_menu();
        function remove_tag_function(){
            $('.remove_tag').click(function(e){
                var this_val = $(this);
                var tag_data = $(this).data();
                if (tag_data.tag && tag_data.message){
                    ajax.jsonRpc('/mail/message_tag_delete', 'call', {
                        message_id: parseInt(tag_data.message),
                        tag_id: parseInt(tag_data.tag),
                    }).then(function(data) {
                          if(!!data.message_tag_list){
                            this_val.closest('.message').find('.message_tag_dropdown_details').html(data.message_tag_dropdown);
                             this_val.closest('.message').find('.message_tag_list_details_body').html(data.message_tag_list);
                            remove_tag_function();
                            tags_dropdown_menu();
                        }
                    });
                }
            });
        }
        remove_tag_function();

        $(".all_mssg_to_tag .tag-dropdown-menu .apply_button a").click(function(e){
            var selected = [];
            $('#wrapper  input.individual:checked').each(function() {
                selected.push($(this).closest('.message__summary').data('message'));
            });
            var tag_ids = new Array();
            var this_val = $(this);
            var message_id = selected;
            var checked_box = $(this).closest('.tag_dropdown').find('input[type="checkbox"]:checked');
            $.each($(checked_box), function (key, value) {
                tag_ids.push(parseInt($(value).val()));
            });
            var create_tag_input = $(this).closest('ul').find('.create_tag_input').val();
            if (message_id.length)
            {
                if (!!create_tag_input)
                {
                    create_tag_input = create_tag_input;
                }
                else
                {
                    create_tag_input = false;
                }
                ajax.jsonRpc('/mail/message_tag_assign/all', 'call', {
                    message_id: message_id,
                    tag_ids: tag_ids,
                    create_tag_input: create_tag_input,
                }).then(function(data) {
                    window.location.reload();
                });
            }
        });
        // $('.all_mssg_to_tag')
        $('.tag_edit_save_btn').click(function(e){
            $(this).closest('form').submit();
        }); 
        $('.tag_delete_save_btn').click(function(e){
            $(this).closest('form').submit();
        });
        $('.folder_edit_save_btn').click(function(e){
            $(this).closest('form').submit();
        }); 
        $('.folder_delete_save_btn').click(function(e){
            $(this).closest('form').submit();
        });
        $('.create_folder_input, .folder-dropdown-menu .apply_button').click(function(e) {
            e.stopPropagation();
        });

        $('.create_snooze_input, .gmail_snooze_child_menu .snooze').click(function(e) {
            e.stopPropagation();
        });

        $('.button-fullscreen').click(function(){
            if($(this).closest('#newmail').hasClass('fullscreenmsger_cl')){
                $(this).closest('#newmail').removeClass("fullscreenmsger_cl");
                $(this).find("i").removeClass('fa fa-compress').addClass('fa fa-expand');
                $(this).attr('title', 'Expand to full-screen');
            }else{
                $(this).find("i").removeClass('fa fa-expand').addClass('fa fa-compress');
                $(this).attr('title', 'Exit full-screen');
                $(this).closest('#newmail').addClass("fullscreenmsger_cl");
                $(this).closest('#newmail').removeClass("fix_mail_hight_cl");
                $(".button-minimize").find("i").removeClass('fa fa-window-maximize').addClass('fa fa-minus');
                $(".button-minimize").attr('title', 'Minimize');
            }
            
        });
        $(".button-minimize").click(function(){
            if($(this).closest('#newmail').hasClass('fix_mail_hight_cl')){
                $(this).closest('#newmail').removeClass("fix_mail_hight_cl");
                $(this).find("i").removeClass('fa fa-window-maximize').addClass('fa fa-minus');
                $(this).attr('title', 'Minimize');
                // $(".button-fullscreen").find("i").removeClass('fa fa-expand').addClass('fa fa-compress');
                // $(".button-fullscreen").attr('title', 'Exit full-screen');
            }else{
                $(this).find("i").removeClass('fa fa-minus').addClass('fa fa-window-maximize');
                $(this).attr('title', 'Maximize');
                $(this).closest('#newmail').addClass("fix_mail_hight_cl");
                $(this).closest('#newmail').removeClass("fullscreenmsger_cl");
                $(".button-fullscreen").find("i").removeClass('fa fa-compress').addClass('fa fa-expand');
                $(".button-fullscreen").attr('title', 'Expand to full-screen');
            }
        });

        $(".open_newmail").click(function(){
            $("#newmail").show();
            if($("#newmail").hasClass('fix_mail_hight_cl')){
                $("#newmail").removeClass("fix_mail_hight_cl");
                $(".button-fullscreen").find("i").removeClass('fa fa-compress').addClass('fa fa-expand')
                $(".button-fullscreen").attr('title', 'Expand to full-screen');
                $(".button-minimize").find("i").removeClass('fa fa-window-maximize').addClass('fa fa-minus')
                $(".button-minimize").attr('title', 'Minimize');
            }
            if($(this).hasClass('message_forwad open_newmail')){
                // var this_partner = $(this).parent().parent().find('.message__details__body_user_name').data('partner');
                var subject = $(this).parent().parent().parent().parent().parent().parent().find('.main_subject').data('subject');
                
                var e_from = $(this).closest('.message__details').find('.address_dropdown table .email_from')[0].innerHTML;
                var e_date = $(this).closest('.message__details').find('.message__details__body:last').find('.body_content').find('.body_mail_id_date').find('.date_content').find('span')[0].innerHTML;
                var e_to = $(this).closest('.message__details').find('.address_dropdown table .email_to')[0].innerHTML;
                var e_body = $(this).closest('.message__details').find('.message__details__body:last').find('.body_content').find('.message__details__body__content')[0].innerHTML;
                var mssg_body = "<br/>" + "<br/>" + "---------- Forwarded message ---------" + "<br/>" + "From: " + "<b>" + e_from + "</b>" + "<br/>" + "Date: " + e_date + "<br/>" + "Subject: " + subject + "<br/>" + "To: " + "<b>" + e_to + "</b>" + "<br/>" + "<br/>" + e_body + "<br/>"

                var attachments = $(this).parent().parent().parent().find('.image_src').val()
                // if (this_partner){
                //     this_partner = this_partner.trim();
                //     $('#compose_partner option').each(function() {
                //         if ($(this).text() == this_partner){
                //             $('#compose_partner').select2('val', $(this).val());
                //         }
                //     });
                // }
                if (subject){
                    $('#gmail_compose_subject').val(subject);
                }else{
                    $('#gmail_compose_subject').val('');
                }
                if (mssg_body){
                    $(".load_editor").summernote("code", mssg_body);
                }
                if (attachments){
                    $('#compose_attach_result').val(attachments)
                }

                // if(attachments.length > 1){ 
                //    for(var i=0;i<attachments.length;i++) { // We iterate through the selected Files
                //       $("#idFromParentElement").append('<div> id=File'+i+'</div'); // Then we create and append the new div to the parent element of our choice
                //       var fileId = 'File'+i;
                //       $("#fileId").data("file",attachments[i]); //After that we include a data into the div with the selected file.
                //    }
                // }
            }
        });

        $(".mail-option .selectall").click(function(){
            $(".individual").prop("checked",$(this).prop("checked"));
            if ($(this).is(":checked")) {
                $(".all_snooze_bttn").show();
                $(".all_move_to_bttn").show();
                $(".all_mssg_to_trash").show();
                $(".all_mssg_to_tag").show();
                $(".all_mssg_to_done").show();
            } else {
                $(".all_snooze_bttn").hide();
                $(".all_move_to_bttn").hide();
                $(".all_mssg_to_trash").hide();
                $(".all_mssg_to_tag").hide();
                $(".all_mssg_to_done").hide();
            }
        });
        $(".individual").click(function(){
            if ($(this).is(":checked")) {
                $(".all_snooze_bttn").show();
                $(".all_move_to_bttn").show();
                $(".all_mssg_to_trash").show();
                $(".all_mssg_to_tag").show();
                $(".all_mssg_to_done").show();
            } else {
                $(".all_snooze_bttn").hide();
                $(".all_move_to_bttn").hide();
                $(".all_mssg_to_trash").hide();
                $(".all_mssg_to_tag").hide();
                $(".all_mssg_to_done").hide();
            }
        });

        $('.movetofolder').on('click', function() {
            var selected = [];
            $('#wrapper  input.individual:checked').each(function() {
                selected.push($(this).closest('.message__summary').data('message'));
            });
            var folder_id = $(this).data('folder_id');
            ajax.jsonRpc('/mail/all_move_to_folder', 'call', {
                messg_ids: selected,
                folder_id: folder_id,
            }).then(function() {
                window.location.reload();
            });
        });

        $('.all_mssg_starred').on('click', function() {
            var mssg_starred = [];
            $(this).parents().find('input.individual:checked').each(function() {
                mssg_starred.push($(this).closest('.message__summary').data('message'));
            });

            ajax.jsonRpc('/mail/all_mssg_starred', 'call', {
                action: 'add',
                messg_ids: mssg_starred,
            }).then(function() {
                window.location.reload();
            });
        });

        $('.all_mssg_unstarred').on('click', function() {
            var mssg_unstarred = [];
            $(this).parents().find('input.individual:checked').each(function() {
                mssg_unstarred.push($(this).closest('.message__summary').data('message'));
            });

            ajax.jsonRpc('/mail/all_mssg_unstarred', 'call', {
                action: 'remove',
                messg_ids: mssg_unstarred,
            }).then(function() {
                window.location.reload();
            });
        });

        $('.all_mssg_unread').on('click', function() {
            var mssg_unread = [];
            $(this).parents().find('input.individual:checked').each(function() {
                mssg_unread.push($(this).closest('.message__summary').data('message'));
            });

            ajax.jsonRpc('/mail/all_mssg_unread', 'call', {
                messg_ids: mssg_unread,
            }).then(function() {
                window.location.reload();
            });
        });

        $('.all_mssg_read').on('click', function() {
            var mssg_read = [];
            $(this).parents().find('input.individual:checked').each(function() {
                mssg_read.push($(this).closest('.message__summary').data('message'));
            });

            ajax.jsonRpc('/mail/all_mssg_read', 'call', {
                messg_ids: mssg_read,
            }).then(function() {
                window.location.reload();
            });
        });
        $(".gmail_snooze_child_menu").on('click', 'a', function(){
            var mssg_snooze = [];
            $(this).parents().find('input.individual:checked').each(function() {
                mssg_snooze.push($(this).closest('.message__summary').data('message'));
            });
            var your_time;
            if($(this).hasClass('snooze_later_today')){
                your_time = 'today'
            }
            if($(this).hasClass('snooze_tomorrow')){
                your_time = 'tomorrow'
            }
            if($(this).hasClass('snooze_nexweek')){
                your_time = 'nexweek'
            }
            ajax.jsonRpc('/mail/all_mssg_snoozed', 'call', {
                mssg_snooze: mssg_snooze,
                your_time: your_time,
            }).then(function() {
                window.location.reload();
            });
        });
        $('.snooze_date_submit').on('click', function() {
            var mssg_snooze = [];
            $(this).parents().find('input.individual:checked').each(function() {
                mssg_snooze.push($(this).closest('.message__summary').data('message'));
            });
            var snooze_datepicker = $('#snoozedatePicker').val();
            ajax.jsonRpc('/mail/all_mssg_snoozed_submit', 'call', {
                mssg_snooze: mssg_snooze,
                snooze_date: snooze_datepicker,
            }).then(function() {
                window.location.reload();
            });
        });
        $('.all_mssg_to_trash').on('click', function() {
            var mssg_trash = [];
            $(this).parents().find('input.individual:checked').each(function() {
                mssg_trash.push($(this).closest('.message__summary').data('message'));
            });
            ajax.jsonRpc('/mail/all_mssg_trash', 'call', {
                messg_ids: mssg_trash,
            }).then(function() {
                window.location.reload();
            });
        });

        $('.all_mssg_to_done').on('click', function() {
            var mssg_done = [];
            $('#wrapper  input.individual:checked').each(function() {
                mssg_done.push($(this).closest('.message__summary').data('message'));
            });
            ajax.jsonRpc('/mail/all_mssg_done', 'call', {
                messg_ids: mssg_done,
            }).then(function() {
                window.location.reload();
            });
        });
        if (($(window).width() >= 767)) {
            $('#menu').css({
                'display': 'block'
            })
        }
        if (($(window).width() < 768)) {
            $('#menu').css({
                'display': 'none'
            })
        }
    });
});