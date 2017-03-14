from ckan.lib import base
from ckan.common import c, _
from ckan import logic
from ckanext.requestdata import emailer
from ckan.plugins import toolkit
import ckan.model as model
import ckan.plugins as p
import json

get_action = logic.get_action
NotFound = logic.NotFound
NotAuthorized = logic.NotAuthorized
ValidationError = logic.ValidationError
abort = base.abort
BaseController = base.BaseController


class RequestDataController(BaseController):

    def send_request(self):
        '''Send mail to resource owner.

        :param data: Contact form data.
        :type data: object

        :rtype: json
        '''
        print "Entered"
        context = {'model': model, 'session': model.Session,
                   'user': c.user, 'auth_user_obj': c.userobj}

        try:
            if p.toolkit.request.method == 'POST':
                data = dict(toolkit.request.POST)
                content = data["message_content"]
                to = data['email_address']
                mail_subject = "Request data"
                get_action('requestdata_request_create')(context, data)
        except NotAuthorized:
            abort(403, _('Unauthorized to update this dataset.'))
        except ValidationError:
            error = {
                'success': False,
                'error': {
                    'message': 'An error occurred while requesting the data.'
                }
            }

            return json.dumps(error)

        response_message = emailer.send_email(content, to, mail_subject)

        return json.dumps(response_message)