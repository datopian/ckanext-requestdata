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

NotFound = logic.NotFound
NotAuthorized = logic.NotAuthorized
ValidationError = logic.ValidationError
abort = base.abort
BaseController = base.BaseController

def _get_context():
    return {
        'model': model,
        'session': model.Session,
        'user': c.user or c.author,
        'auth_user_obj': c.userobj
    }

def _get_action(action, data_dict):
    return toolkit.get_action(action)(_get_context(), data_dict)

def _get_email_configuration(user_name,data_owner, dataset_name,email,message,organization):
    schema = logic.schema.update_configuration_schema()
    avaiable_terms =['{name}','{data_owner}','{dataset}','{organization}','{message}','{email}']
    new_terms = [user_name,data_owner,dataset_name,organization,message,email]

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
        if avaiable_terms[i] == '{dataset}' and new_terms[i]:
            url = toolkit.url_for(controller='package', action='read', id=new_terms[i], qualified=True)
            new_terms[i] = '<a href="' + url + '">' + new_terms[i] + '</a>'

        email_header = email_header.replace(avaiable_terms[i],new_terms[i])
        email_body = email_body.replace(avaiable_terms[i],new_terms[i])
        email_footer = email_footer.replace(avaiable_terms[i],new_terms[i])

    url = toolkit.url_for('requestdata_my_requests', id=data_owner, qualified=True)
    email_body += '<br><br> Go to your <a href="' + url + '">My Requests</a> page to see the new request.'
    organizations = _get_action('organization_list_for_user', {'id': data_owner})

    package = _get_action('package_show', {'id': dataset_name})

    for org in organizations:
        if org['name'] in organization and package['owner_org'] == org['id']:
            url = toolkit.url_for('requestdata_organization_requests', id=org['name'], qualified=True)
            email_body += '<br><br> Go to <a href="' + url + '">Requested data</a> page in organization admin.'

    result = email_header + '<br><br>' + email_body + '<br><br>' + email_footer
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
                _get_action('requestdata_request_create', data)
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
        package = _get_action('package_show', data_dict)

        user_obj = context['auth_user_obj']
        user_name = user_obj.fullname
        data_dict = {
            'id': user_obj.id
        }
        organizations = _get_action('organization_list_for_user', data_dict)

        orgs = []
        for i in organizations:
                orgs.append(i['display_name'])
        org = ','.join(orgs)
        dataset_name = package['name']
        email = user_obj.email
        message = data['message_content']
        creator_user_id = package['creator_user_id']
        data_owner = _get_action('user_show', {'id': creator_user_id}).get('name')
        content = _get_email_configuration(user_name,data_owner,dataset_name,email,message,org)
        if len(get_sysadmins()) > 0:
            sysadmin = get_sysadmins()[0].name
            context_sysadmin = {
                'model': model,
                'session': model.Session,
                'user': sysadmin,
                'auth_user_obj': c.userobj
            }
            to = package['maintainer']
            if to is None:
                message = {
                    'success': False,
                    'error': {
                        'fields': {
                            'email': 'Dataset maintainer email not found.'
                        }
                    }
                }

                return json.dumps(message)
            maintainers = to.split(',')
            data_dict = {
                'users' : []
            }
            users_email = []
            #Get users objects from maintainers list
            for id in maintainers:
                user = toolkit.get_action('user_show')(context_sysadmin, {'id': id})
                if user:
                    data_dict['users'].append(user)
                    users_email.append(user['email'])
            mail_subject = config.get('ckan.site_title') + ': New data request'
            response_message = emailer.send_email(content, users_email, mail_subject)

            #notify package creator that new data request was made
            _get_action('requestdata_notification_create', data_dict)
            data_dict = {
                'package_id' : data['package_id'],
                'flag' : 'request'
            }
            _get_action('requestdata_increment_request_data_counters',data_dict)
            return json.dumps(response_message)
        else:
            message = {
                'success': True,
                'message': 'Request sent, but email message was not sent.'
            }

            return json.dumps(message)
