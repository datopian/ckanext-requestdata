from email_validator import validate_email

from ckan.plugins.toolkit import _


def email_validator(key, data, errors, context):
    email = data[key]

    try:
        validate_email(email)
    except Exception:
        message = _('Please provide a valid email address.')
        errors[key].append(message)
