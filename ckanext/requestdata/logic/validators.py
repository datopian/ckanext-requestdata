from email_validator import validate_email

from ckan.plugins.toolkit import _


def email_validator(key, data, errors, context):
    email = data[key]

    try:
        validate_email(email)
    except Exception:
        message = _('Please provide a valid email address.')
        errors[key].append(message)


def state_validator(key, data, errors, context):
    possible_state = ['new', 'open', 'archive']

    if data[key] not in possible_state:
        message = _('The state parameter must be new, open or archive.')
        errors[key].append(message)


def boolean_validator(key, data, errors, context):
    if not isinstance(data[key], bool):
        message = _('The {0} parameter must be a Boolean value.'
                    .format(key[0]))
        errors[key].append(message)
