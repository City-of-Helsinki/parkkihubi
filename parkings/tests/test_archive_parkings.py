import datetime

import pytest
from django.core.management import call_command
from django.test import override_settings
from django.utils import timezone

from parkings.factories import HistoryParkingFactory, ParkingFactory
from parkings.management.commands import archive_parkings
from parkings.models import ArchivedParking, Parking
from parkings.tests.utils import call_mgmt_cmd_with_output

admin_timezone_override = override_settings(ADMIN_TIME_ZONE=None)


def setup_module():
    admin_timezone_override.enable()


def teardown_module():
    admin_timezone_override.disable()


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
    # Create 20 parkings where:
    #  - first ten are older than 1 month, but not over 2 months old
    #  - second ten are older than 2 months
    for age_in_days in [50, 80]:
        time_end = timezone.now() - datetime.timedelta(days=age_in_days)
        HistoryParkingFactory.create_batch(10, time_end=time_end)

    assert ArchivedParking.objects.all().count() == 0
    call_command(archive_parkings.Command(), "--keep-months", months)
    assert ArchivedParking.objects.all().count() == result


@pytest.mark.django_db
@pytest.mark.parametrize('dry_run_enabled, expected_line', [
    (True, "Would have archived 10 parkings"),
    (False, "Archived 10 parkings"),
])
def test_archive_parkings_mgmt_cmd_dry_run(dry_run_enabled, expected_line):
    end_time = timezone.now() - datetime.timedelta(days=60)
    HistoryParkingFactory.create_batch(10, time_end=end_time)
    dry_run_opts = ["--dry-run"] if dry_run_enabled else []

    (result, stdout, stderr) = call_mgmt_cmd_with_output(
        archive_parkings.Command, '-m1', '-v0', *dry_run_opts
    )

    assert expected_line in stdout
