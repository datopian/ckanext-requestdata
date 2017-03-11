from ckan.lib import base
from ckan.common import c, request, _
from ckan import logic
import ckan.model as model
import ckan.lib.helpers as h
import ckan.plugins as p
import json

get_action = logic.get_action
NotFound = logic.NotFound
NotAuthorized = logic.NotAuthorized

abort = base.abort
BaseController = base.BaseController


class RequestDataController(BaseController):

    def send_request(self):
        '''Send mail to resource owner.

        :param data: Contact form data.
        :type data: object

        '''

        context = {'model': model, 'session': model.Session,
                   'user': c.user, 'auth_user_obj': c.userobj}

        try:
            if p.toolkit.request.method == 'POST':
                data_dict = json.loads(p.toolkit.request.body)
                get_action('requestdata_request_create')(context, data_dict)
        except NotAuthorized:
            abort(403, _('Unauthorized to update this dataset.'))
