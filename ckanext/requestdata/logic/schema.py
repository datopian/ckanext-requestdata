from ckan.plugins import toolkit

from ckanext.requestdata.logic import validators


not_missing = toolkit.get_validator('not_missing')
not_empty = toolkit.get_validator('not_empty')
boolean_validator = toolkit.get_validator('boolean_validator')
package_name_exists = toolkit.get_validator('package_name_exists')
email_validator = validators.email_validator


def request_create_schema():
    return {
        'sender_name': [not_empty, unicode],
        'organization': [not_empty, unicode],
        'email_address': [not_empty, email_validator],
        'message_content': [not_empty, unicode],
        'package_name': [not_empty, package_name_exists],
        'data_shared': [not_missing, boolean_validator]
    }
