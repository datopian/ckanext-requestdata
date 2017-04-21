'use strict';

/* add-dataset-modal
 *
 * This JavaScript module handles showing/hiding the add dataset modal.
 *
 */

this.ckan.module('add-dataset-modal', function($) {
  return {
    initialize: function() {
      $.proxyAll(this, /_on/)

      this.el.on('click', this._onAddDatasetClick)

      this.datasetModal = $('.add-dataset-modal')
      this.datasetModalBackdrop = $('.add-dataset-modal-backdrop')
      this.dismissButton = this.datasetModal.find('button[data-dismiss="modal"]')

      this.datasetModalBackdrop.on('click', this._onCloseModal)
      this.dismissButton.on('click', this._onCloseModal)
    },
    _onAddDatasetClick: function(event) {
      this.datasetModal.show()
      this.datasetModalBackdrop.show()
    },
    _onCloseModal(event) {
      this.datasetModal.hide()
      this.datasetModalBackdrop.hide()
    }
  }
})
