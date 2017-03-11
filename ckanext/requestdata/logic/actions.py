from ckan.plugins import toolkit
from ckan.logic import check_access, NotFound
import ckan.lib.navl.dictization_functions as df
from ckan.common import request

from ckanext.requestdata.logic import schema
from ckanext.requestdata.model import ckanextRequestdata


def request_create(context, data_dict):
    '''Create new request data.

    :param sender_name: The name of the sender who request data.
    :type sender_name: string

    :param organization: The sender's organization.
    :type organization: string

    :param email_address: The sender's email_address.
    :type email_address: string

    :param message_content: The content of the message.
    :type message_content: string

    :param package_name: The name of the package the data belongs to.
    :type package_name: string

    :returns: the newly created request data
    :rtype: dictionary

    '''

    check_access('requestdata_request_create', context, data_dict)

    data, errors = df.validate(data_dict, schema.request_create_schema(),
                               context)

    if errors:
        raise toolkit.ValidationError(errors)

    sender_name = data.get('sender_name')
    organization = data.get('organization')
    email_address = data.get('email_address')
    message_content = data.get('message_content')
    package_name = data.get('package_name')

    package = toolkit.get_action('package_show')(context, {'id': package_name})
    package_creator_id = package['creator_user_id']

    model = context['model']
    sender_user_id = model.User.get(context['user']).id

    data = {
        'sender_name': sender_name,
        'sender_user_id': sender_user_id,
        'organization': organization,
        'email_address': email_address,
        'message_content': message_content,
        'package_name': package_name,
        'package_creator_id': package_creator_id
    }

    requestdata = ckanextRequestdata(**data)
    requestdata.save()

    out = requestdata.as_dict()

    return out


@toolkit.side_effect_free
def request_show(context, data_dict):
    '''Return the metadata of a requestdata.

    :param id: The id of a requestdata.
    :type id: string

    :rtype: dictionary

    '''

    # This code is in a try/except clause because when running the tests it
    # gives the error "TypeError: No object (name: request) has been
    # registered for this thread"
    try:
        if request.method != 'GET':
            return {
                'error': {
                    'message': 'Please use HTTP method GET for this action.'
                }
            }
    except TypeError:
        pass

    data, errors = df.validate(data_dict, schema.request_show_schema(),
                               context)

    if errors:
        raise toolkit.ValidationError(errors)

    check_access('requestdata_request_show', context, data_dict)

    id = data.get('id')

    requestdata = ckanextRequestdata.get(key='id', value=id)

    if requestdata is None:
        raise NotFound('Request with provided \'id\' cannot be found')

    out = requestdata.as_dict()

    return out


@toolkit.side_effect_free
def request_list(context, data_dict):
    '''Returns a list of requests.

    :param id: The id of a requestdata.
    :type id: string

    :rtype: list of dictionaries

    '''

    # This code is in a try/except clause because when running the tests it
    # gives the error "TypeError: No object (name: request) has been
    # registered for this thread"
    try:
        if request.method != 'GET':
            return {
                'error': {
                    'message': 'Please use HTTP method GET for this action.'
                }
            }
    except TypeError:
        pass

    check_access('requestdata_request_list', context, data_dict)

    user_id = context['auth_user_obj'].id

    data = {
        'package_creator_id': user_id
    }

    requests = ckanextRequestdata.search(**data)

    out = []

    for item in requests:
        out.append(item.as_dict())

    return out


def request_patch(self):
    pass


def request_update(self):
    pass


def request_delete(self):
    pass
