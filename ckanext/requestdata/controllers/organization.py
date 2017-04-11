from ckan.lib import base
from ckan import logic, model
from ckan.plugins import toolkit
from ckan.common import c, _, request
from ckan.controllers import organization
from collections import Counter

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
        request_params = request.params.dict_of_lists()
        filtered_maintainers = []

        for item in request_params:
            if item == 'filter_by_maintainers':
                for x in request_params[item]:
                    params = x.split('|')
                    org = params[0].split(':')[1]
                    maintainers = params[1].split(':')[1].split(',')
                    maintainers_ids = []

                    if maintainers[0] != '*all*':
                        for i in maintainers:
                            user = _get_action('user_show', {'id': i})
                            maintainers_ids.append(user['id'])

                        data = {
                            'org': org,
                            'maintainers': maintainers_ids
                        }

                        filtered_maintainers.append(data)

        maintainers = []

        for item in requests:
            package = _get_action('package_show', {'id': item['package_id']})
            package_maintainer_ids = package['maintainer'].split(',')
            data_dict = {'id': package['owner_org']}
            org = _get_action('organization_show', data_dict)

            for maint_id in package_maintainer_ids:
                user = _get_action('user_show', {'id': maint_id})
                username = user['name']
                name = user['fullname']

                if not name:
                    name = username

            payload = {'id': maint_id, 'name': name, 'username': username}
            maintainers.append(payload)

        copy_of_maintainers = maintainers
        maintainers = dict((item['id'], item) for item in maintainers).values()
        organ = _get_action('organization_show', {'id': id})

        # Count how many requests each maintainer has
        for main in maintainers:
            count = Counter(item for dct in copy_of_maintainers for item in dct.items())
            main['count'] = count[('id', main['id'])]

        # Sort maintainers by number of requests
        maintainers = sorted(maintainers, key=lambda k: k['count'], reverse=True)

        for i, r in enumerate(requests[:]):
            maintainer_found = False

            package = _get_action('package_show', {'id': r['package_id']})
            package_maintainer_ids = package['maintainer'].split(',')

            data_dict = {'id': package['owner_org']}
            organ = _get_action('organization_show', data_dict)

            # Check if current request is part of a filtered maintainer
            for x in filtered_maintainers:
                if x['org'] == organ['name']:
                    for maint in x['maintainers']:
                        if maint in package_maintainer_ids:
                            maintainer_found = True

                    if not maintainer_found:
                        requests.remove(r)

        # order_by = request.query_string
        # reverse = True
        # order = ''

        # if order_by is not '':
        #     if 'shared' in order_by:
        #         order = 'shared'
        #     elif 'requests' in order_by:
        #         order = 'requests'
        #     elif 'asc' in order_by:
        #         reverse = False
        #         order = 'title'
        #     elif 'desc' in order_by:
        #         reverse = True
        #         order = 'title'

        #     for item in requests:
        #         package = _get_action('package_show', {'id': item['package_id']})
        #         count = _get_action('requestdata_request_data_counters_get', {'package_id': item['package_id']})
        #         item['title'] = package['title']
        #         item['shared'] = count.shared
        #         item['requests'] = count.requests

        #     requests = sorted(requests, key=lambda x: x[order], reverse=reverse)

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
            'requests_archive': requests_archive,
            'maintainers': maintainers,
            'org_name': organ['name']
        }

        self._setup_template_variables(context, {'id': id},
                                       group_type=group_type)

        return render('requestdata/organization_requested_data.html',
                      extra_vars)
