from ckan.plugins.toolkit import _


def request_create(context, data_dict):
    user = context['user']

    if user:
        return {'success': True}
    else:
        message = _('Only registered users can request data.')

        return {'success': False, 'msg': message}
