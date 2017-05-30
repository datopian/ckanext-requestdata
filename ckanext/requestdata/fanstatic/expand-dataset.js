(function() {

  var archiveRequestsArrow = $('.archive-requests-arrow')

  archiveRequestsArrow.on('click', function(event) {
    var arrow = $(this)
    var iconRight = 'icon-chevron-right' 
    var iconDown = 'icon-chevron-down'
    var prefix = ''

    if (archiveRequestsArrow.hasClass('glyphicon')) {
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
  })

})()
