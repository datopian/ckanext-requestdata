from pylons import request

from ckan.controllers import api


class ApiController(api.ApiController):
    def members_for_org_autocomplete(self):
        params = dict(request.params)

        print 'params'
