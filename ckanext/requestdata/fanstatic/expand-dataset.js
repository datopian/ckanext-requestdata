(function() {

  var archiveRequestsArrow = $('.archive-requests-arrow')

  archiveRequestsArrow.on('click', function(event) {
    var arrow = $(this)

    if (arrow.hasClass('icon-chevron-right')) {
      arrow.removeClass('icon-chevron-right')
      arrow.addClass('icon-chevron-down')
    } else if (arrow.hasClass('icon-chevron-down')) {
      arrow.removeClass('icon-chevron-down')
      arrow.addClass('icon-chevron-right')
    }
  })

})()
