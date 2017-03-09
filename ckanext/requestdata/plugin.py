import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit

from ckanext.requestdata.model import setup as model_setup
from ckanext.requestdata.logic import actions
from ckanext.requestdata.logic import auth


class RequestdataPlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.IRoutes, inherit=True)
    plugins.implements(plugins.IConfigurable)
    plugins.implements(plugins.IActions)
    plugins.implements(plugins.IAuthFunctions)

    # IConfigurer

    def update_config(self, config_):
        toolkit.add_template_directory(config_, 'templates')
        toolkit.add_public_directory(config_, 'public')
        toolkit.add_resource('fanstatic', 'requestdata')

    # IRoutes

    def before_map(self, map):
        controller =\
            'ckanext.requestdata.controllers.package:PackageController'

        map.connect('/dataset/make_active/{pkg_name}', controller=controller,
                    action='make_active')

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
            'requestdata_request_show': auth.request_show
        }
