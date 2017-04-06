from email_validator import validate_email

from ckan.plugins.toolkit import _
from ckan.plugins.toolkit import get_action


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


def members_in_org_validator(key, data, errors, context):
    maintainers = data[key].split(',')
    model = context['model']
    owner_org = data[('owner_org',)]
    data_dict = {
        'id': owner_org
    }

    members_in_org = get_action('member_list')(context, data_dict)

    # member_list returns more than just users, so we need to extract only
    # users
    members_in_org = [member for member in members_in_org
                      if member[1] == 'user']

    for email in maintainers:
        user = model.User.by_email(email)
        user_found = False

        if len(user) > 0:
            user = user[0]

            for member in members_in_org:
                if member[0] == user.id:
                    user_found = True

            if not user_found:
                message = _('The user with email "{0}" is not part of this '
                            'organization.'.format(email))
                errors[key].append(message)
        else:
            message = _('The user with email "{0}" does not exist.'
                        .format(email))
            errors[key].append(message)


def request_counter_validator(key, data, errors, context):
    counters = ['request','replied','declined','shared']
    if data[key] not in counters:
        message = _('The flag parameter must be request, replied, declined, or shared')
        errors[key].append(message)