import json

from paste.deploy.converters import asbool
from pylons import config

from ckan.lib import base
from ckan import logic, model
from ckan.plugins import toolkit
from ckan.common import c, _
from ckan import authz
import ckan.lib.helpers as h

from ckanext.requestdata.emailer import send_email

get_action = logic.get_action
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


class UserController(BaseController):

    def my_requested_data(self, id):
        '''Handles creating template for 'My Requested Data' page in the
        user's dashboard.

        :param id: The user's id.
        :type id: string

        :returns: template

        '''

        try:
            requests = _get_action('requestdata_request_list_for_current_user',
                                   {})
        except NotAuthorized:
            abort(403, _('Not authorized to see this page.'))

        c.is_myself = id == c.user

        if not c.is_myself:
            abort(403, _('Not authorized to see this page.'))

        requests_new = []
        requests_open = []
        requests_archive = []

        for item in requests:
            if item['state'] == 'new':
                requests_new.append(item)
            elif item['state'] == 'open':
                requests_open.append(item)
            elif item['state'] == 'archive':
                requests_archive.append(item)

        extra_vars = {
            'requests_new': requests_new,
            'requests_open': requests_open,
            'requests_archive': requests_archive
        }

        data_dict = {
            'id': id,
            'include_num_followers': True
        }

        context = _get_context()
        user_obj = context['auth_user_obj']
        user_id = user_obj.id
        notify_seen = _get_action('requestdata_notification_change', user_id)
        self._setup_template_variables(_get_context(), data_dict)

        return toolkit.render('requestdata/my_requested_data.html', extra_vars)

    def _setup_template_variables(self, context, data_dict):
        c.is_sysadmin = authz.is_sysadmin(c.user)
        try:
            user_dict = get_action('user_show')(context, data_dict)
        except NotFound:
            abort(404, _('User not found'))
        except NotAuthorized:
            abort(403, _('Not authorized to see this page'))

        c.user_dict = user_dict
        c.about_formatted = h.render_markdown(user_dict['about'])

    def handle_new_request_action(self, username, request_action):
        '''Handles sending email to the person who created the request, as well
        as updating the state of the request depending on the data sent.

        :param username: The user's name.
        :type username: string

        :param request_action: The current action. Can be either reply or
        reject
        :type request_action: string

        :rtype: json

        '''

        data = dict(toolkit.request.POST)

        if 'rejected' in data:
            data['rejected'] = asbool(data['rejected'])

        message_content = data.get('message_content')

        if message_content is None or message_content == '':
            payload = {
                'success': False,
                'error': {
                    'message_content': 'Missing value'
                }
            }

            return json.dumps(payload)

        try:
            _get_action('requestdata_request_patch', data)
        except NotAuthorized:
            abort(403, _('Not authorized to use this action.'))
        except ValidationError as e:
            error = {
                'success': False,
                'error': {
                    'fields': e.error_dict
                }
            }

            return json.dumps(error)

        to = data['send_to']

        subject = config.get('ckan.site_title') + ': Data request ' +\
            request_action

        file = data.get('file_upload')

        response = send_email(message_content, to, subject, file=file)

        if response['success'] is False:
            error = {
                'success': False,
                'error': {
                    'fields': {
                        'email': response['message']
                    }
                }
            }

            return json.dumps(error)

        success = {
            'success': True,
            'message': 'Message was sent successfully'
        }

        return json.dumps(success)

    def handle_open_request_action(self, username, request_action):
        '''Handles updating the state of the request depending on the data
        sent.

        :param username: The user's name.
        :type username: string

        :param request_action: The current action. Can be either shared or
        notshared
        :type request_action: string

        :rtype: json

        '''

        data = dict(toolkit.request.POST)

        if 'data_shared' in data:
            data['data_shared'] = asbool(data['data_shared'])

        if data['data_shared'] == 'true':
            data['data_shared'] = True
        elif data['data_shared'] == 'false':
            data['data_shared'] = False

        try:
            _get_action('requestdata_request_patch', data)
        except NotAuthorized:
            abort(403, _('Not authorized to use this action.'))
        except ValidationError as e:
            error = {
                'success': False,
                'error': {
                    'fields': e.error_dict
                }
            }

            return json.dumps(error)

        success = {
            'success': True,
            'message': 'Request\'s state successfully updated.'
        }

        return json.dumps(success)
