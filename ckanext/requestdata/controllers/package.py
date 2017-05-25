from ckan.lib import base
from ckan.common import c, _
from ckan import logic
import ckan.model as model
import ckan.lib.helpers as h
from ckan.plugins import toolkit
from ckan.controllers.package import PackageController as _PackageController

from ckanext.requestdata.helpers import has_query_param

get_action = logic.get_action
NotAuthorized = logic.NotAuthorized
ValidationError = logic.ValidationError

redirect = base.redirect
abort = base.abort


class PackageController(_PackageController):

    def create_metadata_package(self):

        # Handle metadata-only datasets
        if has_query_param('metadata'):
            package_type = 'requestdata-metadata-only'
            form_vars = {
                'errors': {},
                'dataset_type': package_type,
                'action': 'new',
                'error_summary': {},
                'data': {
                    'tag_string': '',
                    'group_id': None,
                    'type': package_type
                },
                'stage': ['active']
            }

            if toolkit.request.method == 'POST':
                context = {'model': model, 'session': model.Session,
                           'user': c.user, 'auth_user_obj': c.userobj}

                data_dict = dict(toolkit.request.POST)
                data_dict['type'] = package_type

                try:
                    package = get_action('package_create')(context, data_dict)

                    url = h.url_for(controller='package', action='read',
                                    id=package['name'])

                    redirect(url)
                except NotAuthorized:
                    abort(403, _('Unauthorized to create a dataset.'))
                except ValidationError, e:
                    errors = e.error_dict
                    error_summary = e.error_summary

                    form_vars = {
                        'errors': errors,
                        'dataset_type': package_type,
                        'action': 'new',
                        'error_summary': error_summary,
                        'stage': ['active']
                    }

                    form_vars['data'] = data_dict

                    extra_vars = {
                        'form_vars': form_vars,
                        'form_snippet': 'package/new_package_form.html',
                        'dataset_type': package_type
                    }

                    return toolkit.render('package/new.html',
                                          extra_vars=extra_vars)
            else:
                return self.new()
        else:
            return self.new()
