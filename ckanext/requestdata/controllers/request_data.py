from ckan.lib import base
from ckan.common import c, _
from ckan import logic
from ckanext.requestdata import emailer
from ckan.plugins import toolkit
from ckan.controllers.admin import get_sysadmins
try:
    # CKAN 2.7 and later
    from ckan.common import config
except ImportError:
    # CKAN 2.6 and earlier
    from pylons import config
import ckan.model as model
import ckan.plugins as p
import json


get_action = logic.get_action
NotFound = logic.NotFound
NotAuthorized = logic.NotAuthorized
ValidationError = logic.ValidationError
abort = base.abort
BaseController = base.BaseController

def _get_email_congiuration(user_name,dataset_name,email,message,organization):

    schema = logic.schema.update_configuration_schema()
    avaiable_terms =['{name}','{dataset}','{organization}','{message}','{email}']
    new_terms = [user_name,dataset_name,email,message,organization]

    for key in schema:
        ##get only email configuration
        if 'email_header' in key:
            email_header = config.get(key)
        elif 'email_body' in key:
            email_body = config.get(key)
        elif 'email_footer' in key:
            email_footer = config.get(key)
    if '{message}' not in email_body and not email_body and not email_footer:
        email_body += message
        return email_body
    for i in range(0,len(avaiable_terms)):
            email_header = email_header.replace(avaiable_terms[i],new_terms[i])
            email_body = email_body.replace(avaiable_terms[i],new_terms[i])
            email_footer = email_footer.replace(avaiable_terms[i],new_terms[i])
    result = email_header + '\n' + email_body + '\n' + email_footer
    return result

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
                #a = _get_email_congiuration()
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

        user_obj = context['auth_user_obj']
        user_name = user_obj.fullname
        data_dict = {
            'id': user_obj.id
        }
        organizations = get_action('organization_list_for_user')(context, data_dict)
        orgs = []
        for i in organizations:
                orgs.append(i['display_name'])
        org = ','.join(orgs)
        dataset_name = package['name']
        email = user_obj.email
        message = data['message_content']
        content = _get_email_congiuration(user_name,dataset_name,email,message,org)
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
