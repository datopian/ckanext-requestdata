import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit


class RequestdataPlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.IRoutes, inherit=True)

    # IConfigurer

    def update_config(self, config_):
        toolkit.add_template_directory(config_, 'templates')
        toolkit.add_public_directory(config_, 'public')
        toolkit.add_resource('fanstatic', 'requestdata')

    # IMapper

    def before_map(self, map):
        controller =\
            'ckanext.requestdata.controllers.package:PackageController'

        map.connect('/dataset/make_active/{pkg_name}', controller=controller,
                    action='make_active')

        return map
