import dateutil.parser
from django.utils import timezone
from rest_framework.exceptions import ValidationError


def parse_timestamp_or_now(timestamp_string):
    """
    Parse given timestamp string or return current time.

    If the timestamp string is falsy, return current time, otherwise try
    to parse the string and return the parsed value.

    :type timestamp_string: str
    :rtype: datetime.datetime
    :raises rest_framework.exceptions.ValidationError: on parse error
    """
    if not timestamp_string:
        return timezone.now()
    return parse_timestamp(timestamp_string)


def parse_timestamp(datetime_string):
    try:
        return dateutil.parser.parse(datetime_string)
    except (ValueError, OverflowError):
        raise ValidationError('Invalid timestamp: {}'.format(datetime_string))
