'use strict';

/* modal-form
 *
 * This JavaScript module creates a modal and responds to from actions
 *
 */

this.ckan.module('modal-form', function ($) {
  return {
    initialize: function() {
      $.proxyAll(this, /_on/);

      this.el.on('click', this._onClick);
    },
    // Whether or not the rendered snippet has already been received from CKAN.
    _snippetReceived: false,
    _onClick: function(event) {
      if (!this._snippetReceived) {
        this.sandbox.client.getTemplate(this.options.template_file, {}, this._onReceiveSnippet);
        this._snippetReceived = true;
      }
    },
    _onReceiveSnippet: function(html) {
      this.sandbox.body.append(this.createModal(html));
      this.modal.modal('show');
    },
    createModal: function(html) {
      if (!this.modal) {
        var element = this.modal = jQuery(html);
        element.on('click', '.btn-primary', this._onConfirmSuccess);
        element.on('click', '.btn-cancel', this._onConfirmCancel);
        element.modal({show: false});
      }

      return this.modal;
    },
    _onConfirmSuccess: function(event) {
      this.performAction();
    },
    _onConfirmCancel: function(event) {
      this.modal.modal('hide');
      this._snippetReceived = false;
    }
  };
});
