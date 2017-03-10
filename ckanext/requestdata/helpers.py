import timeago
import datetime


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
