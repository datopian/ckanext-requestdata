import datetime

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

    :param package_id: The id of the package the data belongs to.
    :type package_id: string

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
    package_id = data.get('package_id')

    package = toolkit.get_action('package_show')(context, {'id': package_id})
    package_creator_id = package['creator_user_id']

    model = context['model']
    sender_user_id = model.User.get(context['user']).id

    data = {
        'sender_name': sender_name,
        'sender_user_id': sender_user_id,
        'organization': organization,
        'email_address': email_address,
        'message_content': message_content,
        'package_id': package_id,
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

    requestdata = ckanextRequestdata.get(id=id)

    if requestdata is None:
        raise NotFound('Request with provided \'id\' cannot be found')

    out = requestdata.as_dict()

    return out


@toolkit.side_effect_free
def request_list_for_organization(context, data_dict):
    '''Returns a list of requests for specified organization.

    :param org_id: The organization id.
    :type org_id: string

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

    check_access('requestdata_request_list_for_current_user',
                 context, data_dict)

    data, errors = df.validate(data_dict,
                               schema.request_list_for_organization_schema(),
                               context)

    if errors:
        raise toolkit.ValidationError(errors)

    org_id = data.get('org_id')

    data_dict = {
        'fq': 'organization:' + org_id,
        'include_private': True
    }

    packages = toolkit.get_action('package_search')(context, data_dict)
    total_requests = []

    for package in packages['results']:
        data = {
            'package_id': package['id']
        }
        requests = ckanextRequestdata.search(**data)

        for item in requests:
            total_requests.append(item.as_dict())

    return total_requests


@toolkit.side_effect_free
def request_list_for_current_user(context, data_dict):
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

    check_access('requestdata_request_list_for_current_user',
                 context, data_dict)

    user_id = context['auth_user_obj'].id

    data = {
        'package_creator_id': user_id
    }

    requests = ckanextRequestdata.search(**data)

    out = []

    for item in requests:
        out.append(item.as_dict())

    return out


def request_patch(context, data_dict):
    '''Patch a request.

    :param id: The id of a request.
    :type id: string

    :returns: A patched request
    :rtype: dictionary

    '''

    request_patch_schema = schema.request_patch_schema()
    fields = request_patch_schema.keys()

    # Exclude fields from the schema that are not in data_dict
    for field in fields:
        if field not in data_dict.keys() and\
           (field != 'id' and field != 'package_id'):
            request_patch_schema.pop(field)

    data, errors = df.validate(data_dict, request_patch_schema, context)

    if errors:
        raise toolkit.ValidationError(errors)

    check_access('requestdata_request_patch', context, data_dict)

    id = data.get('id')
    package_id = data.get('package_id')

    payload = {
        'id': id,
        'package_id': package_id
    }

    request = ckanextRequestdata.get(**payload)

    if request is None:
        raise NotFound

    request_patch_schema.pop('id')
    request_patch_schema.pop('package_id')

    fields = request_patch_schema.keys()

    for field in fields:
        setattr(request, field, data.get(field))

    request.modified_at = datetime.datetime.now()

    request.save()

    out = request.as_dict()

    return out


def request_update(self):
    pass


def request_delete(self):
    pass
