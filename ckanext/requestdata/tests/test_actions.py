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
    def test_create_requestdata_valid(self):
        package = factories.Dataset(name='test_dataset')
        user = factories.User()
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

        assert result['package_id'] == data_dict['package_id']
        assert result['sender_name'] == data_dict['sender_name']
        assert result['message_content'] == data_dict['message_content']
        assert result['organization'] == data_dict['organization']
        assert result['email_address'] == data_dict['email_address']
        assert result['package_creator_id'] == package['creator_user_id']
        assert result['sender_user_id'] == user['id']
        assert result['state'] == 'new'
        assert result['data_shared'] is False

    def test_create_requestdata_missing_values_raises_error(self):
        with assert_raises(logic.ValidationError) as cm:
            helpers.call_action('requestdata_request_create')

        ex = cm.exception

        assert len(ex.error_dict) == 5

        assert ex.error_dict['message_content'] == ['Missing value']
        assert ex.error_dict['organization'] == ['Missing value']
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

    def test_show_requestdata_valid(self):
        package = factories.Dataset(name='test_dataset')
        user = factories.User()
        context = {'user': user['name']}
        data_dict = {
            'package_id': package['id'],
            'sender_name': 'John Doe',
            'message_content': 'I want to add additional data.',
            'organization': 'Google',
            'email_address': 'test@test.com',
        }

        result = helpers.call_action('requestdata_request_create',
                                     context, **data_dict)

        requestdata_id = result['id']

        data_dict_show = {
            'id': requestdata_id,
            'package_id': data_dict['package_id']
        }

        result = helpers.call_action('requestdata_request_show',
                                     **data_dict_show)

        assert result['package_id'] == data_dict['package_id']
        assert result['sender_name'] == data_dict['sender_name']
        assert result['message_content'] == data_dict['message_content']
        assert result['organization'] == data_dict['organization']
        assert result['email_address'] == data_dict['email_address']
        assert result['data_shared'] is False
        assert result['state'] == 'new'
        assert result['package_creator_id'] == package['creator_user_id']
        assert result['sender_user_id'] == user['id']

    def test_show_requestdata_missing_values(self):
        with assert_raises(logic.ValidationError) as cm:
            helpers.call_action('requestdata_request_show')

        ex = cm.exception

        assert ex.error_dict['id'] == ['Missing value']
        assert ex.error_dict['package_id'] == ['Missing value']

    def test_show_requestdata_invalid_package(self):
        data_dict = {
            'package_id': 'non_existing_package_id'
        }

        with assert_raises(logic.ValidationError) as cm:
            helpers.call_action('requestdata_request_show', **data_dict)

        ex = cm.exception

        assert ex.error_dict['package_id'] ==\
            ['Not found: Dataset']

    def test_show_requestdata_request_not_found(self):
        package = factories.Dataset(name='test_dataset')

        data_dict = {
            'id': 'non_existing_id',
            'package_id': package['id']
        }

        with assert_raises(logic.NotFound) as cm:
            helpers.call_action('requestdata_request_show', **data_dict)

        ex = cm.exception

        assert ex.message == 'Request with provided \'id\' cannot be found'

    @raises(logic.NotAuthorized)
    def test_show_requestdata_raises_auth_error(self):
        package = factories.Dataset(name='test_dataset')

        context = {'ignore_auth': False}

        data_dict = {
            'id': 'non_existing_id',
            'package_id': package['id']
        }

        helpers.call_action('requestdata_request_show', context=context,
                            **data_dict)

    def test_requestdata_request_list_for_current_user(self):
        package = factories.Dataset(name='test_dataset')
        user = factories.User()
        context = {'user': user['name']}
        data_dict = {
            'package_id': package['id'],
            'sender_name': 'John Doe',
            'message_content': 'I want to add additional data.',
            'organization': 'Google',
            'email_address': 'test@test.com',
        }

        # Create 10 requests.
        for i in range(10):
            helpers.call_action('requestdata_request_create',
                                     context=context, **data_dict)

        user = helpers.call_action('user_show', id=package['creator_user_id'])
        context = {'user': user['name']}

        result = helpers.call_action('requestdata_request_list_for_current_user',
                                     context=context)

        assert len(result) == 10

    def test_requestdata_request_list_for_organization(self):
        org = factories.Organization(name='test_org')
        user = factories.User()
        context = {'user': user['name']}
        data_dict = {
            'sender_name': 'John Doe',
            'message_content': 'I want to add additional data.',
            'organization': 'Google',
            'email_address': 'test@test.com',
        }

        package_ids = []

        for i in range(5):
            package = factories.Dataset(owner_org=org['name'])
            package_ids.append(package['id'])

        # Create one request for each dataset.
        for i in range(5):
            data_dict['package_id'] = package_ids[i]
            helpers.call_action('requestdata_request_create',
                                     context=context, **data_dict)

        result = helpers.call_action('requestdata_request_list_for_organization',
                                     org_id=org['id'])

        assert len(result) == 5
