import timeago
import datetime

from ckan import model, logic
from ckan.common import c, _
from ckan.lib import base
from ckan.plugins import toolkit

NotFound = logic.NotFound
NotAuthorized = logic.NotAuthorized
ValidationError = logic.ValidationError


def _get_context():
    return {
        'model': model,
        'session': model.Session,
        'user': c.user or c.author,
        'auth_user_obj': c.userobj
    }


def _get_action(action, data_dict):
    return toolkit.get_action(action)(_get_context(), data_dict)


def time_ago_from_datetime(date):
    '''Returns a 'time ago' string from an instance of datetime or datetime
    formated string.

    Example: 2 hours ago

    :param date: The parameter which will be formated.
    :type idate: datetime or string

    :rtype: string

    '''

    now = datetime.datetime.now()

    if isinstance(date, datetime.date):
        date = date.strftime("%Y-%m-%d %H:%M:%S")
    elif isinstance(date, str):
        date = date[:-7]

    return timeago.format(date, now)


def get_package_title(package_id):
    try:
        package = _get_action('package_show', {'id': package_id})
    except NotAuthorized:
        base.abort(403, _('Not authorized to see this package.'))
    except NotFound:
        base.abort(403, _('Package not found.'))

    return package['title']
