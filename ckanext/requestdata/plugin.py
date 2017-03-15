import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit

from ckanext.requestdata.model import setup as model_setup
from ckanext.requestdata.logic import actions
from ckanext.requestdata.logic import auth
from ckanext.requestdata import helpers


class RequestdataPlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.IRoutes, inherit=True)
    plugins.implements(plugins.IConfigurable)
    plugins.implements(plugins.IActions)
    plugins.implements(plugins.IAuthFunctions)
    plugins.implements(plugins.ITemplateHelpers)

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
            'requestdata_request_list': actions.request_list,
            'requestdata_request_patch': actions.request_patch,
            'requestdata_request_update': actions.request_update,
            'requestdata_request_delete': actions.request_delete
        }

    # IAuthFunctions

    def get_auth_functions(self):
        return {
            'requestdata_request_create': auth.request_create,
            'requestdata_request_show': auth.request_show,
            'requestdata_request_list': auth.request_list,
            'requestdata_request_patch': auth.request_patch
        }

    # ITemplateHelpers

    def get_helpers(self):
        return {
            'requestdata_time_ago_from_datetime':
                helpers.time_ago_from_datetime,
            'requestdata_get_package_title':
                helpers.get_package_title
        }
