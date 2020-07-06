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
    var $el = $(ev.target.parentElement).parents('.vision_upload').find('.response');
    $el.html('');
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

        ajax.jsonRpc('/vision/response', 'call', data).then(function (resp) {
          if (resp) {
            $el.html(resp.datas);
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
