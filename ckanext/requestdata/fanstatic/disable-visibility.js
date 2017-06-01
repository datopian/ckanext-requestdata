(function() {
  var visibilitySelect = document.querySelector('#field-private')

  // Select the "Public" option
  visibilitySelect.selectedIndex = 1

  // For some reason, other script is reenabling the select, so we need to add
  // a timeout
  setTimeout(function() {
    visibilitySelect.setAttribute('disabled', 'disabled')
  }, 500)
})()
