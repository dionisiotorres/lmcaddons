/* Copyright (c) 2016-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>) */
/* See LICENSE file for full copyright and licensing details. */
/* License URL : https://store.webkul.com/license.html/ */

odoo.define('website_advertisement_manager.website_ad', function(require) {
    "use strict";
    var ajax = require('web.ajax');

    $(document).ready(function(){


        $('[id^=adblockMultiple]').carousel({
          interval: 10000
        })

        $('[id^=adblockMultiple] .carousel-item').each(function(){
          var next = $(this).next();

          if (!next.length) {
            next = $(this).siblings(':first');
          }
          next.children(':first-child').clone().appendTo($(this));
          if (next.next().length>0) {
            next.next().children(':first-child').clone().appendTo($(this));
          }
          else {
          	$(this).siblings(':first').children(':first-child').clone().appendTo($(this));
          }
        });

        $('.ad_img_browse_btn').click(function(){
            $('#imgUpload').trigger('click');
        });

        $("#portal_add_banner").on("click", function(){
            var block_id = parseInt($(this).data('block-id'))
            var ad_banner_link = document.getElementById("ad_banner_link").value
            var ele = document.getElementById("imgUpload")
            var files = !!ele.files ? ele.files : [];
            // if (!files.length || !window.FileReader) return;

            if($("#ad_file_name").text().trim() == ""){
                $("#ad_banner_link").removeClass('ad_link_error')
                $("#imgUpload").parent().addClass('image_error')
                $("#show_req_panel").css("display", "inline-block")
            }
            else if(ad_banner_link==''){
                $("#imgUpload").parent().removeClass('image_error')
                $("#ad_banner_link").addClass('ad_link_error')
                $("#show_req_panel").css("display", "inline-block")
            }
            else{
                $("#ad_banner_link").removeClass('ad_link_error')
                $("#imgUpload").parent().removeClass('image_error')
                $("#show_req_panel").css("display", "none")

                if (!(!files.length || !window.FileReader) && (/^image/.test( files[0].type))){
                    var ReaderObj = new FileReader();
                    ReaderObj.readAsDataURL(files[0]);
                    ReaderObj.onloadend = function(){
                        var block = this.result.split(";");
                        var realData = block[1].split(",")[1];
                        var image_name = files[0].name
                        $('.ad_loader').show();
                        ajax.jsonRpc("/set/block/banner", 'call' ,{
                            'block_id': block_id,
                            'image': realData,
                            'ad_banner_link': ad_banner_link,
                            'ad_img_name': image_name,
                        }).then(function(data){
                            $('.ad_loader').hide();
                            location.reload(true);
                            $("#img_success_upd").css("display", "inline-block")
                        })
                    }
                }

                else{
                    $('.ad_loader').show();
                    ajax.jsonRpc("/set/block/banner", 'call' ,{
                        'block_id': block_id,
                        'ad_banner_link': ad_banner_link,
                    }).then(function(data){
                        $('.ad_loader').hide();
                        location.reload(true);
                        $("#img_success_upd").css("display", "inline-block")
                    })
                }
            }
        });

        $("#imgUpload").on("change", function(){
            var files = !!this.files ? this.files : [];
            if (!files.length || !window.FileReader) return; // Check if File is selected, or no FileReader support
            if (/^image/.test( files[0].type)){ //  Allow only image upload
                var ReaderObj = new FileReader(); // Create instance of the FileReader
                ReaderObj.readAsDataURL(files[0]); // read the file uploaded
                ReaderObj.onloadend = function(){ // set uploaded image data as background of div
                    $("#image_preview").css("background-image", "url("+this.result+")");
                    $("#ad_file_name").html(files[0].name)
                }
            }
            else{
                alert("Upload an image");
            }
        });

        $('tr.ad_block_row').click(function() {
            var href = $(this).find("a").attr("href");
            if (href) {
                window.location = href;
          }
        });

        $('.book_ad_block_button').on('click',function (event) {
            var block_id = parseInt($(this).data('block-id'))
            var disabledDates = []
            $('.ad_loader').show();
            ajax.jsonRpc("/book/ad/block", 'call', {
                'block_id': block_id,
            }
            ).then(function (data) {
                var $modal = $(data['website_advertisement_manager.website_ad_block_book_modal'])
                disabledDates = data.block_date_list
                $('.ad_loader').hide();
                $modal.appendTo('#wrap')
                .modal('show')
                .on('shown.bs.modal', function () {
                    $('#input_ad_date_from').datepicker({
                        minDate : new Date(),
                        icons: {
                            time: 'fa fa-clock-o',
                            date: 'fa fa-calendar',
                            next: 'fa fa-chevron-right',
                            previous: 'fa fa-chevron-left',
                            up: 'fa fa-chevron-up',
                            down: 'fa fa-chevron-down',
                        },
                        beforeShowDay: function(date){
                            var string = jQuery.datepicker.formatDate('yy-mm-dd', date);
                            return [ disabledDates.indexOf(string) == -1 ]
                        }
                    });
                    $('#input_ad_date_to').datepicker({
                        minDate : new Date(),
                        icons: {
                            time: 'fa fa-clock-o',
                            date: 'fa fa-calendar',
                            next: 'fa fa-chevron-right',
                            previous: 'fa fa-chevron-left',
                            up: 'fa fa-chevron-up',
                            down: 'fa fa-chevron-down',
                        },
                        beforeShowDay: function(date){
                            var string = jQuery.datepicker.formatDate('yy-mm-dd', date);
                            return [ disabledDates.indexOf(string) == -1 ]
                        }
                    });
                })
                .on('hidden.bs.modal', function () {
                    $(this).remove();
                })
            });
        });

        var $left_el = $(".left_ads");
        if ($left_el.length > 0) {
            $left_el.scrollToFixed({
                minWidth: 990,
                marginTop: 82,
                limit: function () {
                    var limit = $('stopfixedads').offset().top - $left_el.outerHeight(true) - 125;
                    return limit;
                }
            });
        }
        var $right_el = $(".right_ads");
        if ($right_el.length > 0) {
            $right_el.scrollToFixed({
                minWidth: 990,
                marginTop: 82,
                limit: function () {
                    var limit = $('stopfixedads').offset().top - $right_el.outerHeight(true) - 125;
                    return limit;
                }
            });
        }

    });

    $(document).on('change', '#input_ad_date_from , #input_ad_date_to', function(){
        var block_price_unit = $("#AdBlockModal").find('.block_price_unit').find('.oe_currency_value').html()
        var total_amount = $('.block_total_amount').find('.oe_currency_value').text()
        var ad_date_from = moment($("#input_ad_date_from").val().toString(), 'MM/DD/YYYY');
        var ad_date_to = moment($("#input_ad_date_to").val().toString(), 'MM/DD/YYYY');
        var days = ad_date_to.diff(ad_date_from, 'days') + 1
        if (days==NaN || days<0 || days==0){days = 1}
        // if (days<0){days = Math.abs(days)}
        var total_amount = parseFloat(block_price_unit * days).toFixed(2)
        if(total_amount == NaN){
            total_amount = block_price_unit
        }
        if (ad_date_from._i!='' && ad_date_to._i!=''){
            $('.total_days').text(days)
            $('.block_total_amount').find('.oe_currency_value').text(total_amount)
        }
    })

    $(document).on('click', '#block_add_to_cart', function(event){
        event.preventDefault()
        var $form = $(this).closest('form');
        var amount= parseFloat($('.block_price_unit').find('.oe_currency_value').html()).toFixed(2)
        var block_id = parseInt($form.find('input[type="hidden"][name="product_id"]').first().val());
        var ad_date_from = moment($("#input_ad_date_from").val().toString(), 'MM/DD/YYYY');
        var ad_date_to = moment($("#input_ad_date_to").val().toString(), 'MM/DD/YYYY');
        var days = ad_date_to.diff(ad_date_from, 'days')
        var error = 0
        var error_msg = ''

        if(ad_date_from._i=='' || ad_date_to._i==''){
            error = 1
            error_msg = "Dates cannot be blank."
        }
        if(error==1){
            $("#input_ad_date_from").addClass("has_error")
            $("#input_ad_date_to").addClass("has_error")
            $('div.show_error').css("display","");
            $('span.error_msg').text(error_msg)
            $('.total_days').text('1')
            $('.block_total_amount').find('.oe_currency_value').text(amount)
        }
        else{
            $('.ad_loader').show();
            ajax.jsonRpc('/validate/ad/dates', 'call',{
                'block_id': block_id,
                'ad_date_from': $("#input_ad_date_from").val(),
                'ad_date_to': $("#input_ad_date_to").val(),
            }).then(function(data){
                if(data.error){
                    error_msg = data.error_msg
                    $("#input_ad_date_from").addClass("has_error")
                    $("#input_ad_date_to").addClass("has_error")
                    $('div.show_error').css("display","");
                    $('span.error_msg').text(error_msg)
                    $('.total_days').text('1')
                    $('.block_total_amount').find('.oe_currency_value').text(amount)
                }
                else{
                    $("#input_ad_date_from").removeClass("has_error")
                    $("#input_ad_date_to").removeClass("has_error")
                    $('div.show_error').css("display","none");
                    if(event.isDefaultPrevented()){
                        $form.submit();
                    }
                }
                $('.ad_loader').hide();
            })
        }
    });

});
