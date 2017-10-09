from nose.tools import assert_raises, raises

from ckan.tests import helpers, factories
from ckan import plugins, logic

import mock
from mock import patch, call
import unittest
import smtplib
from ckanext.requestdata.emailer import send_email
from ckanext.requestdata import emailer

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

class TestEmailer(ActionBase):

    def test_send_email(self):
        #send_email("test_content", "some@some.com", "Subject_Test")
        #Mock 'smtplib.SMTP' class
        with patch("smtplib.SMTP") as mock_smtp:
            to_address = "aleksandar.ristov@keitaro.com"
            subject = "testSubject"
            content = "testContent"
            send_email(content, to_address, subject)

            #Instanca od mocked SMTP object
            instance = mock_smtp.return_value

            #dali mock e povikana
            self.assertTrue(instance.sendmail.called)

    def test_send_email_no_to_address(self):
        with patch("smtplib.SMTP") as mock_smtp:
            to_address = None
            subject = "testSubject"
            content = "testContent"
            try:
                send_email(content, to_address, subject)
                assert False
            except:
                instance = mock_smtp.return_value
                self.assertFalse(instance.sendmail.called)
