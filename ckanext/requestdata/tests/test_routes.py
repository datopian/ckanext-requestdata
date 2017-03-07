from ckan.tests import helpers, factories
from ckan import plugins


class RoutesBase(object):
    @classmethod
    def setup_class(self):
        self.app = helpers._get_test_app()
        if not plugins.plugin_loaded('requestdata'):
            plugins.load('requestdata')

    def setup(self):
        helpers.reset_db()

    @classmethod
    def teardown_class(self):
        if plugins.plugin_loaded('requestdata'):
            plugins.unload('requestdata')


class TestRoutes(RoutesBase):
    def test_make_dataset_active(self):
        factories.Organization(name='test_org')
        factories.Dataset(owner_org='test_org', name='test_dataset')

        user = factories.Sysadmin()

        headers = {'Authorization': str(user['apikey'])}

        data_dict = {
            'id': 'test_dataset',
            'state': 'draft'
        }

        self.app.post_json('/api/action/package_patch',
                           data_dict, extra_environ=headers)

        data_dict = {
            'pkg_name': 'test_dataset',
        }

        self.app.post_json('/dataset/make_active/test_dataset',
                           data_dict, extra_environ=headers)

        result = helpers.call_action('package_show', id='test_dataset')

        assert result['state'] == 'active'
