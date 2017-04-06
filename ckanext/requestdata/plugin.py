import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit

from ckanext.requestdata.model import setup as model_setup
from ckanext.requestdata.logic import actions
from ckanext.requestdata.logic import auth
from ckanext.requestdata import helpers
from ckanext.requestdata.logic import validators


class RequestdataPlugin(plugins.SingletonPlugin, toolkit.DefaultDatasetForm):
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.IRoutes, inherit=True)
    plugins.implements(plugins.IConfigurable)
    plugins.implements(plugins.IActions)
    plugins.implements(plugins.IAuthFunctions)
    plugins.implements(plugins.ITemplateHelpers)
    plugins.implements(plugins.IDatasetForm)

    # IConfigurer

    def update_config(self, config_):
        toolkit.add_template_directory(config_, 'templates')
        toolkit.add_public_directory(config_, 'public')
        toolkit.add_resource('fanstatic', 'requestdata')

    def update_config_schema(self, schema):
        ignore_missing = toolkit.get_validator('ignore_missing')

        email_body = {}
        email_body.update({'email_header': [ignore_missing, unicode],
                           'email_body': [ignore_missing, unicode],
                           'email_footer': [ignore_missing, unicode]})

        schema.update(email_body)

        return schema

    # IRoutes

    def before_map(self, map):

        package_controller =\
            'ckanext.requestdata.controllers.package:PackageController'
        user_controller =\
            'ckanext.requestdata.controllers.user:UserController'
        request_data_controller = \
            'ckanext.requestdata.controllers.request_data:RequestDataController'
        admin_controller = \
            'ckanext.requestdata.controllers.admin:AdminController'
        organization_controller =\
            'ckanext.requestdata.controllers.organization:OrganizationController'

        api_controller =\
            'ckanext.requestdata.controllers.api:ApiController'

        map.connect('/dataset/make_active/{pkg_name}',
                    controller=package_controller,
                    action='make_active')

        map.connect('requestdata_my_requests',
                    '/user/my_requested_data/{id}',
                    controller=user_controller,
                    action='my_requested_data', ckan_icon='list')

        map.connect('requestdata_handle_new_request_action',
                    '/user/my_requested_data/{username}/' +
                    '{request_action:reply|reject}',
                    controller=user_controller,
                    action='handle_new_request_action')

        map.connect('requestdata_handle_open_request_action',
                    '/user/my_requested_data/{username}/' +
                    '{request_action:shared|notshared}',
                    controller=user_controller,
                    action='handle_open_request_action')

        map.connect('requestdata_send_request','/dataset/send_request', controller=request_data_controller,
                    action='send_request')

        map.connect('ckanadmin_email','/ckan-admin/email', controller=admin_controller,
                    action='email', ckan_icon='envelope-alt')
        map.connect('ckanadmin_requests_data', '/ckan-admin/requests_data', controller=admin_controller,
                    action='requests_data', ckan_icon='list')

        map.connect('download_requests_data', '/ckan-admin/requests_data/download', controller=admin_controller,
                    action='download_requests_data')

        map.connect('requestdata_organization_requests',
                    '/organization/requested_data/{id}',
                    controller=organization_controller,
                    action='requested_data', ckan_icon='list')

        map.connect('members_for_org_autocomplete',
                    '/api/2/util/user/members_for_org_autocomplete',
                    controller=api_controller,
                    action='members_for_org_autocomplete')

        return map

    # IConfigurable

    def configure(self, config):

        # Setup requestdata model
        model_setup()

    # IActions

    def get_actions(self):
        return {
            'requestdata_request_create': actions.request_create,
            'requestdata_request_show': actions.request_show,
            'requestdata_request_list_for_current_user':
            actions.request_list_for_current_user,
            'requestdata_request_list_for_organization':
            actions.request_list_for_organization,
            'requestdata_request_list_for_sysadmin': actions.request_list_for_sysadmin,
            'requestdata_request_patch': actions.request_patch,
            'requestdata_request_update': actions.request_update,
            'requestdata_request_delete': actions.request_delete,
            'requestdata_notification_create': actions.notification_create,
            'requestdata_notification_for_current_user': actions.notification_for_current_user,
            'requestdata_notification_change': actions.notification_change,
            'requestdata_increment_request_data_counters':actions.increment_request_data_counters,
            'requestdata_request_data_counters_get' : actions.request_data_counters_get
        }

    # IAuthFunctions

    def get_auth_functions(self):
        return {
            'requestdata_request_create': auth.request_create,
            'requestdata_request_show': auth.request_show,
            'requestdata_request_list_for_current_user':
            auth.request_list_for_current_user,
            'requestdata_request_list_for_organization':
            auth.request_list_for_organization,
            'requestdata_request_patch': auth.request_patch,
            'requestdata_request_list_for_sysadmin': auth.request_list_for_sysadmin
        }

    # ITemplateHelpers

    def get_helpers(self):
        return {
            'requestdata_time_ago_from_datetime':
                helpers.time_ago_from_datetime,
            'requestdata_get_package_title':
                helpers.get_package_title,
            'requestdata_get_notification':
                helpers.get_notification,
            'requestdata_get_request_counters':
                helpers.get_request_counters
        }

    # IDatasetForm

    def _modify_package_schema(self, schema):
        not_empty = toolkit.get_validator('not_empty')
        convert_to_extras = toolkit.get_converter('convert_to_extras')
        members_in_org_validator = validators.members_in_org_validator

        schema.update({
            'maintainer': [not_empty, members_in_org_validator,
                           convert_to_extras]
        })

        return schema

    def create_package_schema(self):
        schema = super(RequestdataPlugin, self).create_package_schema()
        schema = self._modify_package_schema(schema)

        return schema

    def update_package_schema(self):
        schema = super(RequestdataPlugin, self).update_package_schema()
        schema = self._modify_package_schema(schema)

        return schema

    def show_package_schema(self):
        schema = super(RequestdataPlugin, self).show_package_schema()
        not_empty = toolkit.get_validator('not_empty')
        convert_from_extras = toolkit.get_converter('convert_from_extras')

        schema.update({
            'maintainer': [not_empty, convert_from_extras]
        })

        return schema

    def is_fallback(self):
        # Return True to register this plugin as the default handler for
        # package types not handled by any other IDatasetForm plugin.
        return True

    def package_types(self):
        # This plugin doesn't handle any special package types, it just
        # registers itself as the default (above).
        return []
