import builtins
import datetime
from unittest import mock

import pytest
from django.core.management import call_command
from django.utils import timezone

from parkings.factories import ArchivedParkingFactory
from parkings.management.commands import sanitize_parkings
from parkings.models import ArchivedParking
from parkings.tests.utils import call_mgmt_cmd_with_output


@pytest.mark.django_db
def test_sanitize_parking():
    parking = ArchivedParkingFactory()
    assert parking.sanitized_at is None

    assert ArchivedParking.objects.count() == 1
    sanitized_parking = ArchivedParking.objects.first()
    sanitized_parking.sanitize()

    assert sanitized_parking.registration_number != parking.registration_number
    assert sanitized_parking.registration_number.startswith('!')
    assert sanitized_parking.sanitized_at is not None
    assert sanitized_parking.id == parking.id
    assert sanitized_parking.modified_at == parking.modified_at


@pytest.mark.django_db
@pytest.mark.parametrize('months, result', [(None, 30), (1, 20), (2, 10)])
def test_sanitize_parkings_mgmt_cmd(months, result):
    end_time_1 = timezone.now() - datetime.timedelta(days=60)
    end_time_2 = timezone.now() - datetime.timedelta(days=90)

    ArchivedParkingFactory.create_batch(10, time_end=timezone.now())
    ArchivedParkingFactory.create_batch(10, time_end=end_time_1)
    ArchivedParkingFactory.create_batch(10, time_end=end_time_2)

    assert ArchivedParking.objects.filter(sanitized_at__isnull=True).count() == 30

    if months:
        call_command(sanitize_parkings.Command(), months)
    else:
        call_command(sanitize_parkings.Command())

    assert ArchivedParking.objects.filter(sanitized_at__isnull=False).count() == result


@pytest.mark.django_db
@pytest.mark.parametrize('choice, stdout_result', [('yes', 'Sanitized 10 parkings.'), ('no', '')])
def test_sanitize_parkings_mgmt_cmd_confirm(choice, stdout_result):
    ArchivedParkingFactory.create_batch(10)
    with mock.patch.object(builtins, 'input', lambda _: choice):
        (result, stdout, stderr) = call_mgmt_cmd_with_output(sanitize_parkings.Command, '--confirm')
        assert stdout.rstrip() == stdout_result
