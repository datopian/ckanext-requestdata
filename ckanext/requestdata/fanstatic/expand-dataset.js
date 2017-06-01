/* expand-dataset
 *
 * This JavaScript module handles toggling arrow icon for expand/contract 
 *
 */

this.ckan.module('expand-dataset', function($) {
  return {
    initialize: function() {
      $.proxyAll(this, /_on/)

      this.el.on('click', this._onArrowClick)
    },
    _onArrowClick: function(event) {
      var arrow = this.el.find('i')
      var iconRight = 'icon-chevron-right' 
      var iconDown = 'icon-chevron-down'
      var prefix = ''

      if (arrow.hasClass('glyphicon')) {
        prefix = 'glyph'
      }

      iconRight = prefix + iconRight
      iconDown = prefix + iconDown

      if (arrow.hasClass(iconRight)) {
        arrow.removeClass(iconRight)
        arrow.addClass(iconDown)
      } else if (arrow.hasClass(iconDown)) {
        arrow.removeClass(iconDown)
        arrow.addClass(iconRight)
      }
    }
  }
})

