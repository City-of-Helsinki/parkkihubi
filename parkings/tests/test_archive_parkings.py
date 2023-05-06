import datetime

import pytest
from django.core.management import call_command
from django.test import override_settings
from django.utils import timezone

from parkings.factories import (
    CompleteHistoryParkingFactory, CompleteParkingFactory)
from parkings.management.commands import archive_parkings
from parkings.models import ArchivedParking, Parking
from parkings.tests.utils import call_mgmt_cmd_with_output

admin_timezone_override = override_settings(ADMIN_TIME_ZONE=None)


def setup_module():
    admin_timezone_override.enable()


def teardown_module():
    admin_timezone_override.disable()


def create_ongoing_parkings(count, **kwargs):
    result = CompleteParkingFactory.create_batch(count, **kwargs)
    check_parkings_have_all_fields(result)
    return result


def create_ended_parkings(count, **kwargs):
    result = CompleteHistoryParkingFactory.create_batch(count, **kwargs)
    check_parkings_have_all_fields(result)
    return result


def check_parkings_have_all_fields(parkings):
    for parking in parkings:
        check_parking_has_all_fields(parking)


def check_parking_has_all_fields(parking):
    assert parking.id
    assert parking.created_at
    assert parking.modified_at
    assert parking.region
    assert parking.parking_area
    assert parking.terminal_number
    assert parking.terminal
    assert parking.location
    assert parking.operator
    assert parking.registration_number
    assert parking.normalized_reg_num
    assert parking.time_start
    assert parking.time_end
    assert parking.domain
    assert parking.zone
    assert parking.is_disc_parking in [True, False]


@pytest.mark.django_db
def test_archive_parkings():
    create_ongoing_parkings(10)
    create_ended_parkings(10)

    assert Parking.objects.all().count() == 20
    assert ArchivedParking.objects.all().count() == 0

    end_time = timezone.now() - datetime.timedelta(days=7)
    parkings_to_archive = Parking.objects.ends_before(end_time)
    parkings_to_archive.archive()

    assert Parking.objects.all().count() == 10
    assert ArchivedParking.objects.all().count() == 10


@pytest.mark.django_db
def test_archived_parking_data():
    parking = create_ended_parkings(1)[0]

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
    assert archived_parking.time_start == parking.time_start
    assert archived_parking.time_end == parking.time_end
    assert archived_parking.location == parking.location
    assert archived_parking.region == parking.region
    assert archived_parking.parking_area == parking.parking_area
    assert archived_parking.terminal_number == parking.terminal_number
    assert archived_parking.terminal == parking.terminal
    assert archived_parking.operator == parking.operator
    assert archived_parking.normalized_reg_num == parking.normalized_reg_num
    assert archived_parking.domain == parking.domain
    assert archived_parking.zone == parking.zone
    assert archived_parking.is_disc_parking == parking.is_disc_parking


@pytest.mark.django_db
@pytest.mark.parametrize('months, result', [(1, 20), (2, 10)])
def test_archive_parkings_mgmt_cmd(months, result):
    # Create 20 parkings where:
    #  - first ten are older than 1 month, but not over 2 months old
    #  - second ten are older than 2 months
    for age_in_days in [50, 80]:
        time_end = timezone.now() - datetime.timedelta(days=age_in_days)
        create_ended_parkings(10, time_end=time_end)

    assert ArchivedParking.objects.all().count() == 0
    pre_parking_count = Parking.objects.count()

    call_command(archive_parkings.Command(), "--keep-months", months)

    assert ArchivedParking.objects.all().count() == result
    assert Parking.objects.count() == pre_parking_count - result


@pytest.mark.django_db
@pytest.mark.parametrize('dry_run_enabled, expected_line', [
    (True, "Would have archived 10 parkings"),
    (False, "Archived 10 parkings"),
])
def test_archive_parkings_mgmt_cmd_dry_run(dry_run_enabled, expected_line):
    end_time = timezone.now() - datetime.timedelta(days=60)
    parkings = create_ended_parkings(10, time_end=end_time)
    parking_ids = [x.id for x in parkings]
    dry_run_opts = ["--dry-run"] if dry_run_enabled else []

    (result, stdout, stderr) = call_mgmt_cmd_with_output(
        archive_parkings.Command, '-m1', '-v0', *dry_run_opts
    )

    assert expected_line in stdout
    still_alive_parkings = Parking.objects.filter(id__in=parking_ids)
    if dry_run_enabled:
        assert still_alive_parkings.count() == 10
        assert ArchivedParking.objects.count() == 0
    else:
        assert still_alive_parkings.count() == 0
        assert ArchivedParking.objects.count() == 10
