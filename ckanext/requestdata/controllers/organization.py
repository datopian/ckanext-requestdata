from ckan.lib import base
from ckan import logic, model
from ckan.plugins import toolkit
from ckan.common import c, _, request
from ckan.controllers import organization

get_action = logic.get_action
NotFound = logic.NotFound
NotAuthorized = logic.NotAuthorized
ValidationError = logic.ValidationError

abort = base.abort
render = base.render
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


class OrganizationController(organization.OrganizationController):

    def requested_data(self, id):
        '''Handles creating template for 'Requested Data' page in the
        organization's dashboard.

        :param id: The organization's id.
        :type id: string

        :returns: template

        '''

        try:
            requests = _get_action('requestdata_request_list_for_organization',
                                   {'org_id': id})
        except NotAuthorized:
            abort(403, _('Not authorized to see this page.'))

        group_type = self._ensure_controller_matches_group_type(id)
        context = {
            'model': model,
            'session': model.Session,
            'user': c.user
        }
        c.group_dict = self._get_group_dict(id)
        group_type = c.group_dict['type']

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
                count = _get_action('requestdata_request_data_counters_get', {'package_id': item['package_id']})
                item['title'] = package['title']
                item['shared'] = count.shared
                item['requests'] = count.requests

            requests = sorted(requests, key=lambda x: x[order], reverse=reverse)

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

        self._setup_template_variables(context, {'id': id},
                                       group_type=group_type)

        return render('requestdata/organization_requested_data.html',
                      extra_vars)
