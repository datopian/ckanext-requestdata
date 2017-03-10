"use strict";

/* request-data
 *
 * This JavaScript module adds a Bootstrap popover with contact form
 * that sends mail to the resource owner
 *
 */

this.ckan.module('request-data', function ($) {
  return {
 initialize: function () {

      // proxyAll() ensures that whenever an _on*() function from this
      // JavaScript module is called, the `this` variable in the function will
      // be this JavaScript module object.
      //
      // You probably want to call proxyAll() like this in the initialize()
      // function of most modules.
      //
      // This is a shortcut function provided by CKAN, it wraps jQuery's
      // proxy() function: http://api.jquery.com/jQuery.proxy/
      $.proxyAll(this, /_on/);

      // Add a Bootstrap popover to the button. Since we don't have the HTML
      // from the snippet yet, we just set the content to "Loading..."
      this.el.popover({html: true, content: 'Loading...', placement: 'left'});

      // Add an event handler to the button, when the user clicks the button
      // our _onClick() function will be called.
      this.el.on('click', this._onClick);
    },

    // Whether or not the rendered snippet has already been received from CKAN.
    _snippetReceived: false,

    _onClick: function(event) {

        // Send an ajax request to CKAN to render the popover.html snippet.
        // We wrap this in an if statement because we only want to request
        // the snippet from CKAN once, not every time the button is clicked.
        if (!this._snippetReceived) {
            this.sandbox.client.getTemplate('request_contact.html',
                                            this.options,
                                            this._onReceiveSnippet);
            this._snippetReceived = true;
        }
    },

    // CKAN calls this function when it has rendered the snippet, and passes
    // it the rendered HTML.
    _onReceiveSnippet: function(html) {
      this.sandbox.body.append(this.createModal(html));
      // Replace the popover with a new one that has the rendered HTML from the
      // snippet as its contents.
      this.el.popover('destroy');
      this.el.popover({title: this.options.title, html: true,
                       content: html, placement: 'left'});
      this.el.popover('show');
    },

    createModal: function (html) {
      if (!this.modal) {
        var element = this.modal = jQuery(html);
        element.on('click', '.btn-primary', this._onConfirmSuccess);
        element.on('click', '.btn-cancel', this._onConfirmCancel);
        element.modal({show: false});

        //element.find('h3').text(this.i18n('heading'));
       // element.find('.modal-body').text(this.i18n('content'));
       // element.find('.btn-primary').text(this.i18n('confirm'));
      //  element.find('.btn-cancel').text(this.i18n('cancel'));
      }
      return this.modal;
    },
    _onConfirmSuccess: function (event) {
      this.performAction();
    },

    /* Event handler for the cancel event */
    _onConfirmCancel: function (event) {

    }
  };
});