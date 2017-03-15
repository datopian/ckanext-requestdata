'use strict';

/* handle-open-request
 *
 * This JavaScript module handles actions to an open request.
 *
 */

this.ckan.module('handle-open-request', function($) {
  var api = {
    get: function(action, params) {
        var base_url = ckan.sandbox().client.endpoint
        params = $.param(params)
        var url = base_url + '/api/action/' + action + '?' + params

        return $.getJSON(url)
    },
    post: function(action, data) {
      var base_url = ckan.sandbox().client.endpoint
      var url = base_url + '/api/action/' + action

      return $.post(url, JSON.stringify(data), 'json')
    }
  }

  function _showAlert(message, className, duration) {
    var alert = $('.request-message-alert');

    alert.find('.alert-text').html(message);
    alert.addClass(className);
    alert.show();

    setTimeout(function() {
      alert.hide();
      alert.removeClass(className);
    }, duration);
  }

  return {
    initialize: function() {
      $.proxyAll(this, /_on/)

      this.el.on('click', this._onClick)
    },
    _onClick: function(event) {
      this.el.attr('disabled', 'disabled')

      var base_url = ckan.sandbox().client.endpoint
      var url = base_url + this.options.action || ''
      var payload = this.options.post_data || {}

      $.post(url, payload, 'json')
        .done(function(data) {
          var className = ''
          var message = ''

          data = JSON.parse(data)

          if (data.success) {
            if (payload.data_shared === true) {
              className = 'icon-thumbs-up'
            } else {
              className = 'icon-thumbs-down'
            }

            this.el.html('<i class="' + className + '"></i>')
          } else if (data.error && data.error.fields) {
            for (var key in data.error.fields) {
              message += key + ': ' + data.error.fields[key] + '<br>'
            }

            _showAlert(message, 'alert-danger', 4000)
          }

          this.el.removeAttr('disabled')
        }.bind(this))
        .error(function(error) {
          this.el.removeAttr('disabled')
        }.bind(this))
    }
  }
})
