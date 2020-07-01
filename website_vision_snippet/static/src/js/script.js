odoo.define("website_vision_snippet.script", function (require) {
"use strict";

var core = require('web.core');
var sAnimation = require('website.content.snippets.animation');
var ajax = require('web.ajax');
var qweb = core.qweb;

sAnimation.registry.vision = sAnimation.Class.extend({
  selector: '.vision',
  events: {
      'change #upload_vision_file': '_onUploadVisionFile',
  },
  _onUploadVisionFile: function (ev) {
    var $title = $(ev.target.parentElement).parents('.vision_upload').find('.title');
    var $el = $(ev.target.parentElement).parents('.vision_upload').find('.response');
    var $faces = $(ev.target.parentElement).parents('.vision_upload').find('.faces');
    var $lm = $(ev.target.parentElement).parents('.vision_upload').find('.lm');
    var $logos = $(ev.target.parentElement).parents('.vision_upload').find('.logos');
    var $anno = $(ev.target.parentElement).parents('.vision_upload').find('.anno');
    var $loading = $(ev.target.parentElement).parents('.vision_upload').find('.loading');
    $loading.show();
    var $upload_btn = $(ev.target.parentElement).parents('.vision_upload').find('.upload-container');
    $upload_btn.hide();
    if (ev.target.files && ev.target.files[0]) {
      var reader = new FileReader();
      reader.onload = function (e) {
        $('.z-depth-1-half img').attr('src', e.target.result);

        var data = {
          'fileContents': e.target.result
        };

        ajax.jsonRpc('/check/vision', 'call', data).then(function (resp) {
          if (resp) {
            $title.html('');
            $el.html('');
            $faces.html('');
            $lm.html('');
            $logos.html('');
            $anno.html('');
            $title.append('<h1>IMAGE ANALYSIS</h1>');

            $.each(resp.datass, function(index, data){
              $el.append('<p>' + data + '</p>');
            });

            $.each(resp.faces_datas, function(index, data){
              $faces.append('<p>' + data + '</p>');
            });

            $.each(resp.lm_datas, function(index, data){
              $lm.append('<p>' + data + '</p>');
            });

            $.each(resp.logos_datas, function(index, data){
              $logos.append('<p>' + data + '</p>');
            });

            $.each(resp.anno_datas, function(index, data){
              $anno.append('<p>' + data + '</p>');
            });

            $loading.hide();
            $upload_btn.show();
          }
        });
      };
      reader.readAsDataURL(ev.target.files[0]);
    }
  },
});

});
