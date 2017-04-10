try:
    # CKAN 2.7 and later
    from ckan.common import config
except ImportError:
    # CKAN 2.6 and earlier
    from pylons import config
from ckan.plugins import toolkit
from ckan.controllers.admin import AdminController
from ckan import  model
from ckan.common import c, _
import ckan.lib.base as base
import ckan.lib.helpers as h
import ckan.logic as logic
import csv
import json
from cStringIO import StringIO
from ckan.model.user import User

from ckan.common import response ,request

NotFound = logic.NotFound
NotAuthorized = logic.NotAuthorized

c = base.c
redirect = base.redirect
abort = base.abort

def _get_context():
    return {
        'model': model,
        'session': model.Session,
        'user': c.user or c.author,
        'auth_user_obj': c.userobj
    }

def _get_action(action, data_dict):
    return toolkit.get_action(action)(_get_context(), data_dict)

class AdminController(AdminController):
    ctrl = 'ckanext.requestdata.controllers.admin:AdminController'

    def email(self):
        '''
            Handles creating the email template in admin dashboard.

            :returns template
        '''
        data = request.POST
        if 'save' in data:
            try:
                data_dict = dict(request.POST)
                del data_dict['save']
                data = _get_action('config_option_update',data_dict)
            except logic.ValidationError, e:
                errors = e.error_dict
                error_summary = e.error_summary
                vars = {'data': data, 'errors': errors,
                        'error_summary': error_summary}
                return base.render('admin/email.html', extra_vars=vars)

            h.redirect_to(controller=self.ctrl, action='email')

        schema = logic.schema.update_configuration_schema()
        data = {}
        for key in schema:
            data[key] = config.get(key)

        vars = {'data': data, 'errors': {}}
        return toolkit.render('admin/email.html',extra_vars=vars)

    def requests_data(self):
        '''
            Handles creating template for 'Requested Data' page in the
            admin dashboard.

            :returns: template

        '''
        try:
            requests = _get_action('requestdata_request_list_for_sysadmin', {})
        except NotAuthorized:
            abort(403, _('Not authorized to see this page.'))
        organizations = []
        tmp_orgs = []
        filtered_maintainers = []
        reverse = True
        org = {}
        for item in request.params:
            if item == 'filter_by_maintainers':
                params = request.params[item].split('|')
                org = params[0].split(':')[1]
                maintainers = params[1].split(':')[1]
                data = {
                    'org': org,
                    'maintainers': maintainers.split(',')
                }

                filtered_maintainers.append(data)
            elif item == 'order_by':
                params = request.params[item].split('|')
                order = params[0]
                q_organization = params[1].split(':')[1]
                if 'asc' in order:
                    reverse = False
                    order = 'title'
                elif 'desc' in order:
                    reverse = True
                    order = 'title'

                for x in requests:
                    package = _get_action('package_show', {'id': x['package_id']})
                    count = _get_action('requestdata_request_data_counters_get', {'package_id': x['package_id']})
                    x['title'] = package['title']
                    x['shared'] = count.shared
                    x['requests'] = count.requests
                    data_dict = {'id': package['owner_org']}
                    current_org = _get_action('organization_show', data_dict)
                    x['org_id'] = current_org['id']


        for item in requests:
            package = _get_action('package_show', {'id': item['package_id']})
            package_maintainer_ids = package['maintainer'].split(',')
            maintainer_found = False
            org_found = False

            data_dict = {'id': package['owner_org']}
            org = _get_action('organization_show', data_dict)

            # Check if current request is part of a filtered maintainer
            for x in filtered_maintainers:
                for maint in x['maintainers']:
                    if maint in package_maintainer_ids:
                        maintainer_found = True

                if x['org'] == org['id']:
                    org_found = True

            if org_found and not maintainer_found:
                continue

            # Group requests by organization
            if org['id'] not in tmp_orgs:
                data = {
                    'title': org['title'],
                    'org_id': org['id'],
                    'requests_new': [],
                    'requests_open': [],
                    'requests_archive': []
                }

                if item['state'] == 'new':
                    data['requests_new'].append(item)
                elif item['state'] == 'open':
                    data['requests_open'].append(item)
                elif item['state'] == 'archive':
                    data['requests_archive'].append(item)

                organizations.append(data)
            else:
                current_org = next(item for item in organizations if item['org_id'] == org['id'])

                if item['state'] == 'new':
                    current_org['requests_new'].append(item)
                elif item['state'] == 'open':
                    current_org['requests_open'].append(item)
                elif item['state'] == 'archive':
                    current_org['requests_archive'].append(item)

            tmp_orgs.append(org['id'])

        for org in organizations:
            if org['org_id'] == q_organization:
                org['requests_archive'] = sorted( org['requests_archive'], key=lambda x: x[order], reverse=reverse)

        extra_vars = {
            'organizations': organizations
        }

        return toolkit.render('admin/all_requests_data.html', extra_vars)

    def download_requests_data(self):
        '''
            Handles creating csv or json file from all of the Requested Data

            :returns: json or csv file
        '''

        file_format = request.query_string
        requests = _get_action('requestdata_request_list_for_sysadmin', {})
        s = StringIO()

        if 'json' in file_format.lower():
            response.headerlist = [('Content-Type', 'application/json'), ('Content-Disposition', 'attachment;filename="data_requests.json"')]
            json.dump(requests, s, indent=4)

            return s.getvalue()

        if 'csv' in file_format.lower():
            response.headerlist = [('Content-Type','text/csv'),('Content-Disposition', 'attachment;filename="data_requests.csv"')]
            writer = csv.writer(s)
            header = True
            for k in requests:
                if header:
                    writer.writerow(k.keys())
                    header = False
                writer.writerow(k.values())

            return s.getvalue()
