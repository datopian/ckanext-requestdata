import timeago
import datetime
import itertools
from operator import itemgetter

from ckan import model, logic
from ckan.common import c, _
from ckan.lib import base
from ckan.plugins import toolkit
from ckan.model.user import User

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


def get_notification():
    '''Returns a boolean which indicates if notification was seen or not

      :rtype: bool

      '''

    notification = _get_action('requestdata_notification_for_current_user',{})
    return notification


def get_request_counters(id):
    '''
        Returns a counters for particular request data

       :param package_id: The id of the package the request belongs to.
       :type package_id: string

     '''

    package_id = id
    counters = _get_action('requestdata_request_data_counters_get', {'package_id':package_id})
    return counters


def convert_id_to_email(ids):
    ids = ids.split(',')
    emails = []

    for id in ids:
        user = User.get(id)

        if user:
            emails.append(user.email)

    return ','.join(emails)


def group_archived_requests_by_dataset(requests):
    sorted_requests = sorted(requests, key=itemgetter('package_id'))
    grouped_requests = []

    for key, group in itertools.groupby(sorted_requests, key=lambda x: x['package_id']):
        package = _get_action('package_show', {'id': key})
        package_maintainers_ids = package['maintainer'].split(',')
        maintainers = []

        for item in package_maintainers_ids:
            user = _get_action('user_show', {'id': item})
            payload = {
                'id': item,
                'fullname': user['fullname']
            }
            maintainers.append(payload)

        requests = list(group)
        item_shared = requests[0].get('shared')
        item_requests = requests[0].get('requests')

        data = {
            'package_id': key,
            'title': package['title'],
            'maintainers': maintainers,
            'requests_archived': requests,
            'shared': item_shared,
            'requests': item_requests
        }

        grouped_requests.append(data)

    return grouped_requests
