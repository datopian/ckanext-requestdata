from nose.tools import assert_raises, raises

from ckan.tests import helpers, factories
from ckan import plugins, logic


class ActionBase(object):
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


class TestActions(ActionBase):
    '''
    def test_create_requestdata_valid(self):
        user = factories.User()
        users = [{'name': user['name']}]

        factories.Organization(name='test_org', users=users)

        package = factories.Dataset(owner_org='test_org', name='test_dataset',
                                    maintainer=user['id'])
        context = {'user': user['name']}
        data_dict = {
            'package_id': package['id'],
            'sender_name': 'John Doe',
            'message_content': 'I want to add additional data.',
            'organization': 'Google',
            'email_address': 'test@test.com',
        }

        result = helpers.call_action('requestdata_request_create',
                                     context=context, **data_dict)

        assert 'requestdata_id' in result

    def test_create_requestdata_missing_values_raises_error(self):
        with assert_raises(logic.ValidationError) as cm:
            helpers.call_action('requestdata_request_create')

        ex = cm.exception

        assert len(ex.error_dict) == 4

        assert ex.error_dict['message_content'] == ['Missing value']
        assert ex.error_dict['sender_name'] == ['Missing value']
        assert ex.error_dict['email_address'] == ['Missing value']
        assert ex.error_dict['package_id'] == ['Missing value']

    @raises(logic.NotAuthorized)
    def test_create_requestdata_raises_auth_error(self):
        context = {'ignore_auth': False}
        helpers.call_action('requestdata_request_create', context=context)

    def test_create_requestdata_invalid_email(self):
        data_dict = {
            'package_id': 'some-id',
            'sender_name': 'John Doe',
            'message_content': 'I want to add additional data.',
            'organization': 'Google',
            'email_address': 'non@existing.email',
        }

        with assert_raises(logic.ValidationError) as cm:
            helpers.call_action('requestdata_request_create', **data_dict)

        ex = cm.exception

        assert ex.error_dict['email_address'] ==\
            ['Please provide a valid email address.']

    def test_create_requestdata_invalid_package(self):
        data_dict = {
            'package_id': 'non_existing_package_id',
            'sender_name': 'John Doe',
            'message_content': 'I want to add additional data.',
            'organization': 'Google',
            'email_address': 'test@test.com',
        }

        with assert_raises(logic.ValidationError) as cm:
            helpers.call_action('requestdata_request_create', **data_dict)

        ex = cm.exception

        assert ex.error_dict['package_id'] ==\
            ['Not found: Dataset']
    '''
    def test_create_requestdata_package_id_exist(self):
        user = factories.User()
        users = [{'name': user['name']}]

        factories.Organization(name='test_org', users=users)

        package = factories.Dataset(owner_org='test_org', name='test_dataset',
                                    maintainer=user['id'])
        context = {'user': user['name']}
        data_dict = {
            'package_id': package['id'],
            'sender_name': 'John Doe',
            'message_content': 'I want to add additional data.',
            'organization': 'Google',
            'email_address': 'test@test.com',
        }

        helpers.call_action('requestdata_request_create',
                                     context=context, **data_dict)

        response = helpers.call_action('requestdata_request_create',
                                     context=context, **data_dict)
        print 'TUKA'
        print response

