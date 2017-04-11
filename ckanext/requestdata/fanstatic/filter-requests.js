'use strict';

/* filter-requests
 *
 * This JavaScript module handles filtering requests.
 *
 */

this.ckan.module('filter-requests', function($) {

  return {
    initialize: function() {
      $.proxyAll(this, /_on/)

      this.checkboxes = this.el.find('input[type=checkbox]')
      this._populateCheckboxes()

      this.el.on('click', 'button[data-action]', this._onClick)
    },
    _onClick: function(event) {
      event.stopPropagation()
      event.preventDefault()

      var action = $(event.target).attr('data-action')
      var nextLocation = ''
      var param = ''
      var checked = false
      var params = null
      var paramFound = false

      if (action === 'apply') {
        if (window.location.search == '') {
          params = []
        } else {
          params = window.location.search.split('&')
        }

        if (this.options.type == 'maintainer') {
          param = 'filter_by_maintainers=org:' + this.options.org_name + '|maintainers:'

          this.checkboxes.each(function(i, el) {
            if (el.checked) {
              checked = true
              param += el.value + ','
            }
          })

          if (checked) {

            // Remove the comma at the end of the string
            param = param.slice(0, -1)
          } else {

            // If none of the checkboxes are clicked, show all requests
            param += '*all*'
          }

          params.forEach(function(item, i) {

            // If the current filter is already applied, just update it to
            // prevent duplication
            if (item.indexOf('filter_by_maintainers=org:' + this.options.org_name) > -1) {
              paramFound = true
              params[i] = param
            }
          }.bind(this))
        } else if (this.options.type == 'organization') {
          param = 'filter_by_organizations='

          this.checkboxes.each(function(i, el) {
            if (el.checked) {
              checked = true
              param += el.value + ','
            }
          })

          if (checked) {

            // Remove the comma at the end of the string
            param = param.slice(0, -1)
          } else {
            var copy_params = [].concat(params)

            copy_params.forEach(function(item, i) {
              if (item.indexOf('filter_by_organizations') > -1) {
                params.splice(i, 1)
              }
            })

            if (params[0] && params[0].indexOf('?') === -1) {
              params[0] = '?' + params[0]
            }

            params = params.join('&')

            location.href = location.origin + location.pathname + params
          }

          params.forEach(function(item, i) {

            // If the current filter is already applied, just update it to
            // prevent duplication
            if (item.indexOf('filter_by_organizations') > -1) {
              paramFound = true
              params[i] = param
            }
          }.bind(this))
        }

        // If this is a new param then push it to all params
        if (!paramFound) {
          params.push(param)
        }

        if (params[0].indexOf('?') === -1) {
          params[0] = '?' + params[0]
        }

        params = params.join('&')

        location.href = location.origin + location.pathname + params
      } else if (action === 'reset') {
        this.checkboxes.attr('checked', false)
      }
    },
    // Populate checkboxes for filters depending on the filters applied
    _populateCheckboxes: function() {
      var current_url = location.toString();
      var parameters = [];
      var parameter;
      var query;

      try {
        query = current_url.match(/\?(.+)$/)[1].split('&');

        for (var i = 0; i < query.length; i++) {
          parameter = query[i].split('=');

          if (parameter.length === 1) {
              parameter[1] = '';
          }

          var data = {}

          data[decodeURIComponent(parameter[0])] = decodeURIComponent(parameter[1])

          parameters.push(data)
        }
      } catch(error) {

      }

      parameters.forEach(function(param) {
        var filters;
        var org;
        var maintainers;

        if (param.filter_by_maintainers) {
          filters = param.filter_by_maintainers.split('|')
          org = filters[0].split(':')[1]
          maintainers = filters[1].split(':')[1].split(',')

          if (org === this.options.org_name && maintainers[0] !== '*all*') {
            this.checkboxes.each(function(i, checkbox) {
              if (maintainers.indexOf(checkbox.value) > -1) {
                $(checkbox).attr('checked', true)
              }
            })
          }
        } else if (param.filter_by_organizations) {
          var organizations = param.filter_by_organizations.split(',')

          this.checkboxes.each(function(i, checkbox) {
            if (organizations.indexOf(checkbox.value) > -1) {
              $(checkbox).attr('checked', true)
            }
          })
        }
      }.bind(this))
    }
  }
})
