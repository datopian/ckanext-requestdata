from ckan.tests import helpers, factories
from ckan import plugins, logic
import unittest
from ckanext.requestdata.logic.validators import *


class ActionBase(unittest.TestCase):
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


class TestAuth(ActionBase):
    def test_email_validator_validate_is_true(self):
        key = ('state')
        data = {('state'): 'aleksandar.ristov@keitaro.com'}
        errors = {key: []}
        email_validator(key, data, errors, None)
        if len(errors[key]) == 0:
            assert True
        else:
            assert False

    def test_email_validator_validate_is_false(self):
        key = ('state')
        data = {('state'): 'aleksandar.ristovkeitaro.com'}
        errors = {key: []}
        email_validator(key, data, errors, None)
        if len(errors[key]) == 0:
            assert False
        else:
            assert True

    def test_state_validator_not_in_possible_state(self):
        key = ('state')
        data = {('state'): 'test'}
        errors = {key: []}
        state_validator(key, data, errors, None)
        if len(errors[key]) != 0:
            assert True
        else:
            assert False

    def test_state_validator_in_possible_state(self):
        key = ('state')
        data = {('state'): 'new'}
        errors = {key: []}
        state_validator(key, data, errors, None)
        if len(errors[key]) == 0:
            assert True
        else:
            assert False

        data = {('state'): 'open'}
        errors = {key: []}
        state_validator(key, data, errors, None)
        if len(errors[key]) == 0:
            assert True
        else:
            assert False

        data = {('state'): 'archive'}
        errors = {key: []}
        state_validator(key, data, errors, None)
        if len(errors[key]) == 0:
            assert True
        else:
            assert False

    def test_boolean_validator_is_not_instance(self):
        key = ('state')
        data = {('state'): 'True'}
        errors = {key: []}
        boolean_validator(key, data, errors, None)
        if len(errors[key]) == 0:
            assert True
        else:
            assert False

        data = {('state'): 'False'}
        errors = {key: []}
        boolean_validator(key, data, errors, None)
        if len(errors[key]) == 0:
            assert True
        else:
            assert False

    def test_boolean_validator_wrong_value(self):
        key = 'state'
        data = {'state': '3'}
        errors = {key: []}
        error_msg = "String is not true/false"
        try:
            boolean_validator(key, data, errors, None)
            assert False
        except ValueError as e:
            assert error_msg in e.message

    def test_boolean_validator_string_value(self):
        key = ('state')
        data = {('state'): 'Test'}
        errors = {key: []}
        try:
            boolean_validator(key, data, errors, None)
            assert False
        except ValueError:
            assert True

    def test_request_counter_validator_not_in_counters(self):
        key = ('state')
        data = {('state'): 'test'}
        errors = {key: []}
        request_counter_validator(key, data, errors, None)
        if len(errors[key]) != 0:
            assert True
        else:
            assert False

    def test_request_counter_validator_in_counters(self):
        key = ('state')
        data = {('state'): 'request'}
        errors = {key: []}
        request_counter_validator(key, data, errors, None)
        if len(errors[key]) == 0:
            assert True
        else:
            assert False

        data = {('state'): 'replied'}
        errors = {key: []}
        request_counter_validator(key, data, errors, None)
        if len(errors[key]) == 0:
            assert True
        else:
            assert False

        data = {('state'): 'declined'}
        errors = {key: []}
        request_counter_validator(key, data, errors, None)
        if len(errors[key]) == 0:
            assert True
        else:
            assert False

        data = {('state'): 'shared'}
        errors = {key: []}
        request_counter_validator(key, data, errors, None)
        if len(errors[key]) == 0:
            assert True
        else:
            assert False

        data = {('state'): 'shared and replied'}
        errors = {key: []}
        request_counter_validator(key, data, errors, None)
        if len(errors[key]) == 0:
            assert True
        else:
            assert False
