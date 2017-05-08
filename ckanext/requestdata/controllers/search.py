try:
    # CKAN 2.7 and later
    from ckan.common import config
except ImportError:
    # CKAN 2.6 and earlier
    from pylons import config

is_hdx = config.get('hdx_portal')

if is_hdx:
    from ckanext.hdx_search.controllers.search_controller import HDXSearchController as PackageController
else:
    from ckan.controllers.package import PackageController


class SearchController(PackageController):
    def search_datasets(self):
        if is_hdx:
            return self.search()
        else:
            pass
