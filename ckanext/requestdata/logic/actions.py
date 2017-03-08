from ckan.plugins import toolkit
from ckan.logic import check_access
import ckan.lib.navl.dictization_functions as df

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

    :param data_shared: Whether data is shared or not.
    :type data_shared: boolean

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
    data_shared = data.get('data_shared')

    data = {
        'sender_name': sender_name,
        'organization': organization,
        'email_address': email_address,
        'message_content': message_content,
        'package_name': package_name,
        'data_shared': data_shared
    }

    requestdata = ckanextRequestdata(**data)
    requestdata.save()

    out = requestdata.as_dict()

    return out


def request_show(context, data_dict):
    pass


def request_list(self):
    pass


def request_patch(self):
    pass


def request_update(self):
    pass


def request_delete(self):
    pass
