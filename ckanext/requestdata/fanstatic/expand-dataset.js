(function() {

  var archiveRequestsArrow = $('.archive-requests-arrow')

  archiveRequestsArrow.on('click', function(event) {
    var arrow = $(this)

    if (arrow.hasClass('icon-chevron-down')) {
      arrow.removeClass('icon-chevron-down')
      arrow.addClass('icon-chevron-up')
    } else if (arrow.hasClass('icon-chevron-up')) {
      arrow.removeClass('icon-chevron-up')
      arrow.addClass('icon-chevron-down')
    }
  })

})()
