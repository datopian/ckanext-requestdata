# encoding: utf-8
import nose
from datetime import datetime, timedelta
from ckanext.requestdata import helpers as h
import ckan.plugins as p
from ckan.tests import helpers, factories
from ckan import logic

ok_ = nose.tools.ok_
eq_ = nose.tools.eq_
raises = nose.tools.raises


class ActionBase(object):

    @classmethod
    def setup_class(self):
        self.app = helpers._get_test_app()
        if not p.plugin_loaded('requestdata'):
            p.load('requestdata')

    def setup(self):
        helpers.reset_db()

    @classmethod
    def teardown_class(self):
        if p.plugin_loaded('requestdata'):
            p.unload('requestdata')


class TestHelpers(ActionBase):

    def test_time_ago_from_datetime_valid(self):
        d = datetime.today() - timedelta(days=1)
        eq_(h.time_ago_from_datetime(d), '1 day ago')

    def test_time_ago_from_datetime_valid_string_result(self):
        d = datetime.today() - timedelta(days=2)
        assert isinstance(h.time_ago_from_datetime(d), str)

    def test_convert_id_to_emails_valid(self):
        user = factories.User()
        users = [{'name': user['name']}]
        ids = user['id']
        response = h.convert_id_to_email(ids)
        email = 'test_user_05@ckan.org'
        assert email == response

    def test_convert_id_to_emails_invalid(self):
        ids = '231'
        response = h.convert_id_to_email(ids)
        email = 'test_user_05@ckan.org'
        assert email not in response