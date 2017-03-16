from ckan.lib import base
from ckan.common import c, _
from ckan import logic
from ckanext.requestdata import emailer
from ckan.plugins import toolkit
try:
    # CKAN 2.7 and later
    from ckan.common import config
except ImportError:
    # CKAN 2.6 and earlier
    from pylons import config
import ckan.model as model
import ckan.plugins as p
import json
from ckan.controllers.admin import get_sysadmins

get_action = logic.get_action
NotFound = logic.NotFound
NotAuthorized = logic.NotAuthorized
ValidationError = logic.ValidationError
abort = base.abort
BaseController = base.BaseController

def _get_email_congiuration():
    '''
     Get admin schema from database
    :return:
    '''
    schema = logic.schema.update_configuration_schema()
    email_config = {}
    for key in schema:
        ##get only email configuration
        if "email" in key:
            email_config[key] = config.get(key)
    vars = {'data': email_config, 'errors': {}}
    return vars

class RequestDataController(BaseController):

    def send_request(self):
        '''Send mail to resource owner.

        :param data: Contact form data.
        :type data: object

        :rtype: json
        '''
        context = {'model': model, 'session': model.Session,
                   'user': c.user, 'auth_user_obj': c.userobj}

        try:
            if p.toolkit.request.method == 'POST':
                data = dict(toolkit.request.POST)

                get_action('requestdata_request_create')(context, data)
        except NotAuthorized:
            abort(403, _('Unauthorized to update this dataset.'))
        except ValidationError as e:
            error = {
                'success': False,
                'error': {
                     'fields': e.error_dict
                }
            }

            return json.dumps(error)

        data_dict = {'id': data['package_id']}
        package = get_action('package_show')(context, data_dict)

        if len(get_sysadmins()) > 0:
            sysadmin = get_sysadmins()[0].name
            context_sysadmin = {
                'model': model,
                'session': model.Session,
                'user': sysadmin,
                'auth_user_obj': c.userobj
            }

            data_dict = {'id': package['creator_user_id']}
            user = get_action('user_show')(context_sysadmin, data_dict)

            content = data['message_content']
            to = user['email']
            mail_subject = 'Request data'

            response_message = emailer.send_email(content, to, mail_subject)

            return json.dumps(response_message)
        else:
            message = {
                'success': True,
                'message': 'Request sent, but email message was not sent.'
            }

            return json.dumps(message)
