import json
from operator import attrgetter

from paste.deploy.converters import asbool
from pylons import config

from ckan.lib import base
from ckan import logic, model
from ckan.plugins import toolkit
from ckan.common import c, _, request
from ckan import authz
import ckan.lib.helpers as h

from ckanext.requestdata.emailer import send_email
from ckanext.requestdata import helpers

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

        order_by = request.query_string
        requests_new = []
        requests_open = []
        requests_archive = []
        reverse = True
        order = ''

        if order_by is not '':
            if 'shared' in order_by:
                order = 'shared'
            elif 'requests' in order_by:
                order = 'requests'
            elif 'asc' in order_by:
                reverse = False
                order = 'title'
            elif 'desc' in order_by:
                reverse = True
                order = 'title'

            for item in requests:
                package = _get_action('package_show', {'id': item['package_id']})
                count = _get_action('requestdata_request_data_counters_get',{'package_id':item['package_id']})
                item['title'] = package['title']
                item['shared'] = count.shared
                item['requests'] = count.requests

            requests = sorted(requests, key=lambda x: x[order], reverse=reverse)
        #TODO simplify these
        for item in requests:
            package = _get_action('package_show', {'id': item['package_id']})
            package_maintainers_ids = package['maintainer'].split(',')
            item['title'] = package['title']
            maintainers = []
            for i in package_maintainers_ids:
                user = _get_action('user_show', {'id': i})
                payload = {
                    'id': i,
                    'fullname': user['fullname']
                }
                maintainers.append(payload)
            item['maintainers'] = maintainers
            if item['state'] == 'new':
                requests_new.append(item)
            elif item['state'] == 'open':
                requests_open.append(item)
            elif item['state'] == 'archive':
                requests_archive.append(item)

        grouped_requests_archive = helpers.group_archived_requests_by_dataset(requests_archive)

        extra_vars = {
            'requests_new': requests_new,
            'requests_open': requests_open,
            'requests_archive': grouped_requests_archive
        }

        context = _get_context()
        user_obj = context['auth_user_obj']
        user_id = user_obj.id
        data_dict = {
            'user_id' : user_id
        }
        _get_action('requestdata_notification_change', data_dict)

        data_dict = {
            'id': id,
            'include_num_followers': True
        }
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
        counters_data_dict = {
            'package_id': data['package_id'],
            'flag': ''
        }
        if 'rejected' in data:
            data['rejected'] = asbool(data['rejected'])
            counters_data_dict['flag'] = 'declined'
        else:
            counters_data_dict['flag'] = 'replied'
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

        get_action('requestdata_increment_request_data_counters')({}, counters_data_dict)

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
        data_dict = {
            'package_id': data['package_id'],
            'flag': ''
        }
        if data['data_shared']:
            data_dict['flag'] = 'shared'
        else:
            data_dict['flag'] = 'declined'

        get_action('requestdata_increment_request_data_counters')({}, data_dict)
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
