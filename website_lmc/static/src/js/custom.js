odoo.define('website_lmc.custom', function(require) {
"use strict";
    require('web.dom_ready');
    var ajax = require('web.ajax');

    $('.o_forum_profile_pic_edit').on('click', function(ev) {
        ev.preventDefault();
        $(this).closest('form').find('.o_forum_file_upload').trigger('click');
    });

    $('.o_forum_file_upload').on('change', function() {
        if (this.files.length) {
            var $form = $(this).closest('form');
            var reader = new window.FileReader();
            reader.onload = function(ev) {
                $form.find('.o_forum_avatar_img').attr('src', ev.target.result);
            };
            reader.readAsDataURL(this.files[0]);
            $form.find('#forum_clear_image').remove();
        }
    });

    $('.o_forum_profile_pic_clear').click(function() {
        var $form = $(this).closest('form');
        $form.find('.o_forum_avatar_img').attr("src", "/web/static/src/img/placeholder.png");
        $form.append($('<input/>', {
            name: 'clear_image',
            id: 'forum_clear_image',
            type: 'hidden',
        }));
    });

    $('.user_edit_address').on('click', function () {
        // ev.preventDefault();
        $(this).closest('div.one_kanban').find('form.d-none').submit();
    });

    $('.user_shipping_address_add').on('click', function () {
        // ev.preventDefault();
        $(this).closest('div.one_kanban').find('form.d-block').submit();
    });

    // Account country, state, pin onchange
    if ($(".checkout_autoformat").length) {
        var clickwatch = (function(){
              var timer = 0;
              return function(callback, ms){
                clearTimeout(timer);
                timer = setTimeout(callback, ms);
              };
        })();

        $('.checkout_autoformat').on('change', "select[name='country_id']", function () {
            clickwatch(function() {
                if ($("#country_id").val()) {
                    ajax.jsonRpc("/shop/country_infos/" + $("#country_id").val(), 'call', {mode: 'shipping'}).then(
                        function(data) {
                            // placeholder phone_code
                            //$("input[name='phone']").attr('placeholder', data.phone_code !== 0 ? '+'+ data.phone_code : '');

                            // populate states and display
                            var selectStates = $("select[name='state_id']");
                            // dont reload state at first loading (done in qweb)
                            if (selectStates.data('init')===0 || selectStates.find('option').length===1) {
                                if (data.states.length) {
                                    selectStates.html('');
                                    _.each(data.states, function(x) {
                                        var opt = $('<option>').text(x[1])
                                            .attr('value', x[0])
                                            .attr('data-code', x[2]);
                                        selectStates.append(opt);
                                    });
                                    selectStates.parent('div').show();
                                }
                                else {
                                    selectStates.val('').parent('div').hide();
                                }
                                selectStates.data('init', 0);
                            }
                            else {
                                selectStates.data('init', 0);
                            }

                            // manage fields order / visibility
                            if (data.fields) {
                                if ($.inArray('zip', data.fields) > $.inArray('city', data.fields)){
                                    $(".div_zip").before($(".div_city"));
                                }
                                else {
                                    $(".div_zip").after($(".div_city"));
                                }
                                var all_fields = ["street", "zip", "city", "country_name"]; // "state_code"];
                                _.each(all_fields, function(field) {
                                    $(".checkout_autoformat .div_" + field.split('_')[0]).toggle($.inArray(field, data.fields)>=0);
                                });
                            }
                        }
                    );
                }
            }, 500);
        });
    }
    $("select[name='country_id']").change();

    $('.o_forum_address_delete').click(function() {
        var partner_id = $(this).attr('partner_id');
        var card = $(this).closest('div.one_kanban');
        // debugger;
        ajax.jsonRpc('/partner/delete', 'call', {
            'partner_id': parseInt(partner_id)
        }).then(function (data) {
            if (data.success){
                card.addClass("d-none");
                window.location.reload();
            }else{
                console.log("Active order fail to change");
            }
        });
    });
});