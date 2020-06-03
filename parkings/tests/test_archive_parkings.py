import builtins
import datetime
from unittest import mock

import pytest
from django.core.management import call_command
from django.utils import timezone

from parkings.factories import HistoryParkingFactory, ParkingFactory
from parkings.management.commands import archive_parkings
from parkings.models import ArchivedParking, Parking
from parkings.tests.utils import call_mgmt_cmd_with_output


@pytest.mark.django_db
def test_archive_parkings():
    ParkingFactory.create_batch(10)
    HistoryParkingFactory.create_batch(10)

    assert Parking.objects.all().count() == 20
    assert ArchivedParking.objects.all().count() == 0

    end_time = timezone.now() - datetime.timedelta(days=7)
    parkings_to_archive = Parking.objects.ends_before(end_time)
    parkings_to_archive.archive()

    assert Parking.objects.all().count() == 10
    assert ArchivedParking.objects.all().count() == 10


@pytest.mark.django_db
def test_archived_parking_data():
    parking = HistoryParkingFactory()

    assert Parking.objects.all().count() == 1
    assert ArchivedParking.objects.all().count() == 0

    Parking.objects.ends_before(timezone.now()).archive()

    assert Parking.objects.all().count() == 0
    assert ArchivedParking.objects.all().count() == 1

    archived_parking = ArchivedParking.objects.first()

    assert archived_parking.id == parking.id
    assert archived_parking.created_at == parking.created_at
    assert archived_parking.modified_at == parking.modified_at
    assert archived_parking.registration_number == parking.registration_number
    assert archived_parking.time_end == parking.time_end
    assert archived_parking.location == parking.location


@pytest.mark.django_db
@pytest.mark.parametrize('months, result', [(1, 20), (2, 10)])
def test_archive_parkings_mgmt_cmd(months, result):
    end_time_1 = timezone.now() - datetime.timedelta(days=60)
    end_time_2 = timezone.now() - datetime.timedelta(days=90)

    HistoryParkingFactory.create_batch(10, time_end=end_time_1)
    HistoryParkingFactory.create_batch(10, time_end=end_time_2)

    assert ArchivedParking.objects.all().count() == 0
    call_command(archive_parkings.Command(), months)
    assert ArchivedParking.objects.all().count() == result


@pytest.mark.django_db
@pytest.mark.parametrize('choice, stdout_result', [('yes', 'Archived 10 parkings.'), ('no', '')])
def test_archive_parkings_mgmt_cmd_confirm(choice, stdout_result):
    end_time = timezone.now() - datetime.timedelta(days=60)
    HistoryParkingFactory.create_batch(10, time_end=end_time)
    with mock.patch.object(builtins, 'input', lambda _: choice):
        (result, stdout, stderr) = call_mgmt_cmd_with_output(archive_parkings.Command, 1, '--confirm')
        assert stdout.rstrip() == stdout_result
