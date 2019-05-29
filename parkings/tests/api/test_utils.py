import datetime

import pytest
from freezegun import freeze_time
from rest_framework.exceptions import ValidationError as DrfValidationError

from parkings.api.utils import parse_timestamp, parse_timestamp_or_now


def test_parse_timestamp_or_now_with_val():
    parsed = parse_timestamp_or_now('2000-01-01T20:01:05+0200')
    assert isinstance(parsed, datetime.datetime)
    assert str(parsed) == '2000-01-01 20:01:05+02:00'


@freeze_time('2000-02-29T10:15:22Z')
def test_parse_timestamp_or_now_with_empty():
    parsed = parse_timestamp_or_now('')
    assert isinstance(parsed, datetime.datetime)
    assert str(parsed) == '2000-02-29 10:15:22+00:00'


@freeze_time('2000-02-29T10:15:22Z')
def test_parse_timestamp_or_now_with_none():
    parsed = parse_timestamp_or_now(None)
    assert isinstance(parsed, datetime.datetime)
    assert str(parsed) == '2000-02-29 10:15:22+00:00'


def test_parse_timestamp_with_valid_data():
    parsed = parse_timestamp('2000-02-29T10:15:22-12:00')
    assert isinstance(parsed, datetime.datetime)
    assert str(parsed) == '2000-02-29 10:15:22-12:00'


def test_parse_timestamp_with_invalid_data():
    with pytest.raises(DrfValidationError) as excinfo:
        parse_timestamp('foobar')
    assert excinfo.value.detail == ['Invalid timestamp: foobar']
