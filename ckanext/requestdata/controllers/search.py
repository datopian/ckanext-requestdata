try:
    # CKAN 2.7 and later
    from ckan.common import config
except ImportError:
    # CKAN 2.6 and earlier
    from pylons import config

from paste.deploy.converters import asbool

is_hdx = asbool(config.get('hdx_portal', False))

if is_hdx:
    from ckanext.hdx_search.controllers.search_controller\
        import HDXSearchController as PackageController
else:
    from ckan.controllers.package import PackageController


class SearchController(PackageController):
    def search_datasets(self):
        return self.search()
