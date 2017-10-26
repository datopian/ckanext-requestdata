from nose.tools import assert_raises, raises
from ckan.tests import helpers, factories
from ckan import plugins, logic
import unittest
import ckan.model as model
import ckanext.requestdata.logic.auth as a


class ActionBase(unittest.TestCase):
    @classmethod
    def setup_class(self):
        self.app = helpers._get_test_app()
        if not plugins.plugin_loaded('requestdata'):
            plugins.load('requestdata')
        helpers.reset_db()

    def setup(self):
        helpers.reset_db()

    @classmethod
    def teardown_class(self):
        if plugins.plugin_loaded('requestdata'):
            plugins.unload('requestdata')


class TestAuth(ActionBase):
    def test_request_create_user(self):
        context = {'user': 'test'}
        req = a.request_create(context, None)
        self.assertTrue(req['success'])

    def test_request_create_no_user(self):
        context = {'user': None}
        req = a.request_create(context, None)
        self.assertFalse(req['success'])

    def test_request_list_for_current_user(self):
        r = a.request_list_for_current_user(None, None)
        self.assertTrue(r['success'])

    def test_request_list_for_organization_user_not_in_organization(self):
        u = factories.User()
        u2 = factories.User()
        test_org = factories.Organization(
            users=[
                {'name': u['name'], 'capacity': 'admin'}
            ]
        )
        with assert_raises(logic.NotAuthorized) as e:
            logic.check_access('requestdata_request_list_for_organization',
                               {'user': u2['id']},
                               {'org_id': test_org['id']})

    def test_request_list_for_organization_user_in_organization(self):
        u = factories.User()
        u2 = factories.User()
        test_org = factories.Organization(
            users=[
                {'name': u['name'], 'capacity': 'admin'}
            ]
        )
        with assert_raises(logic.NotAuthorized) as e:
            logic.check_access('requestdata_request_list_for_organization',
                               {'user': u['id']},
                               {'org_id': test_org['id']})

    def test_request_list_for_sysadmin_is_sysadmin(self):
        user = factories.Sysadmin()
        context = {'user': user['name'], 'model': model}
        test_org = factories.Organization(
            users=[
                {'name': user['name'], 'capacity': 'admin'}
            ]
        )
        req = a.request_list_for_sysadmin(context, None)
        self.assertTrue(req['success'])

    def test_request_list_for_sysadmin_is_not_sysadmin(self):
        user = factories.User()
        context = {'user': user['name'], 'model': model}
        test_org = factories.Organization(
            users=[
                {'name': user['name'], 'capacity': 'admin'}
            ]
        )
        req = a.request_list_for_sysadmin(context, None)
        self.assertFalse(req['success'])
