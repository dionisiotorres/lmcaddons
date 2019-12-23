odoo.define('bi_website_odoo_gdpr.gdprrequest', function (require) {
'use strict';
    
    require('web.dom_ready');
    var website = require('website.website');
    var core = require('web.core');
    var base = require('web_editor.base');
    var ajax = require('web.ajax');

    $( ".btn.download" ).each(function(index) {
        $(this).on("click", function(){
            var id = $(this).attr('value'); 
            ajax.jsonRpc("/my/download", 'call', {
                'res_id': id,
            }).then(function (data) {
                $("#downloadreq").modal('show');
            });
        });
    });

    $( ".btn.deleted" ).each(function(index) {
        $(this).on("click", function(){
            var id = $(this).attr('value'); 
            ajax.jsonRpc("/my/deleted", 'call', {
                'res_id': id,
            }).then(function (data) {
                $("#deletereq").modal('show');
            });
        });
    });

    $( ".btn.done" ).each(function(index) {
        $(this).on("click", function(){
            window.location.reload()
        });
    });
});