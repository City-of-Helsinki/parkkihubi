import datetime

import pytest
from django.core.management import call_command
from django.utils import timezone

from parkings.anonymization import anonymize_model
from parkings.factories import (
    ArchivedParkingFactory, ParkingCheckFactory, ParkingFactory)
from parkings.factories.permit import create_permits
from parkings.management.commands import clean_reg_nums
from parkings.models import (
    ArchivedParking, Parking, ParkingCheck, Permit, PermitLookupItem)


@pytest.mark.django_db
@pytest.mark.parametrize('batch, hours, result', [(10, 2, 0), (20, 25, 20)])
def test_anonymization_of_archived_parkings_registration_number(batch, hours, result):
    end_time = timezone.now() - datetime.timedelta(hours=hours)
    ArchivedParkingFactory.create_batch(batch, time_end=end_time)

    anonymize_model(ArchivedParking)

    assert ArchivedParking.objects.filter(registration_number="").count() == result


@pytest.mark.django_db
@pytest.mark.parametrize('batch, hours, result', [(10, 2, 0), (20, 25, 20)])
def test_anonymization_of_parkings_registration_number(batch, hours, result):
    end_time = timezone.now() - datetime.timedelta(hours=hours)
    ParkingFactory.create_batch(batch, time_end=end_time)

    anonymize_model(Parking)

    assert Parking.objects.filter(registration_number="").count() == result


@pytest.mark.django_db
@pytest.mark.parametrize('batch, hours, result', [(10, None, 0), (20, 25, 20)])
def test_anonymization_of_parking_check_registration_number(batch, hours, result):
    parking_checks = ParkingCheckFactory.create_batch(batch)
    if hours:
        created_at = timezone.now() - datetime.timedelta(hours=hours)
        for parking_check in parking_checks:
            parking_check.created_at = created_at
            parking_check.save(update_fields=["created_at"])

    anonymize_model(ParkingCheck)

    assert ParkingCheck.objects.filter(registration_number="").count() == result


def change_subjects_validity_time_to_past(permit, max_count=None):
    end_time = timezone.now() - datetime.timedelta(hours=25)
    start_time = end_time - datetime.timedelta(days=30)
    subjects = permit.subjects
    for subject in (subjects if max_count is None else subjects[:max_count]):
        subject["start_time"] = start_time.isoformat()
        subject["end_time"] = end_time.isoformat()
    permit.save(update_fields=["subjects"])


@pytest.mark.django_db
def test_anonymization_of_permit_registration_number_for_expired_permits(user_factory):
    user = user_factory()
    expired_permit_list = create_permits(owner=user, count=5)
    for permit in expired_permit_list:
        change_subjects_validity_time_to_past(permit)

    anonymize_model(Permit)

    for permit in Permit.objects.all():
        check_permit_is_anonymized(permit)


def check_permit_is_anonymized(permit):
    check_permit_reg_nums(permit, is_anonymized)


def is_anonymized(reg_num):
    return reg_num == ""


def check_permit_reg_nums(permit, check_function):
    reg_nums = [x["registration_number"] for x in permit.subjects]
    assert all(check_function(x) for x in reg_nums), (
        "Some reg nums don't pass the check ({}). Reg nums: {}".format(
            check_function.__name__, reg_nums))
    for subject_item in permit.subject_items.all():
        assert check_function(subject_item.registration_number)
    for lookup_item in permit.lookup_items.all():
        assert check_function(lookup_item.registration_number)


@pytest.mark.django_db
def test_not_ended_permits_are_not_anonymized(user_factory):
    user = user_factory()
    create_permits(owner=user, count=3)
    assert Permit.objects.unanonymized().count() == 3

    anonymize_model(Permit)

    assert Permit.objects.unanonymized().count() == 3
    for permit in Permit.objects.all():
        permit.refresh_from_db()
        check_permit_is_unanonymized(permit)


def check_permit_is_unanonymized(permit):
    check_permit_reg_nums(permit, is_unanonymized)


def is_unanonymized(reg_num):
    return isinstance(reg_num, str) and reg_num.strip() != ""


@pytest.mark.django_db
def test_partly_ended_permits_are_not_anonymized(user_factory):
    """
    Test that permits that are only partly ended are not anonymized.

    This is because the permit is still valid for the other registration
    numbers even if it has ended for one of them.

    Test data will contain:
     * 3 permits which have ended for all registration numbers,
     * 3 permits which have ended for only one registration number, and
     * 3 permits which have not ended for any registration numbers.
    """
    user = user_factory()
    permits = create_permits(owner=user, count=9)
    for permit in permits[:3]:
        change_subjects_validity_time_to_past(permit)
    for permit in permits[3:6]:
        assert len(permit.subjects) > 1
        change_subjects_validity_time_to_past(permit, max_count=1)

    anonymize_model(Permit)

    for permit in permits[:3]:
        permit.refresh_from_db()
        check_permit_is_anonymized(permit)

    for permit in permits[3:]:
        permit.refresh_from_db()
        check_permit_is_unanonymized(permit)

    assert Permit.objects.unanonymized().count() == 6


@pytest.mark.django_db
@pytest.mark.parametrize(
    'batch, hours, result, permit_batch, permit_result',
    [(10, 2, 0, 20, 60), (20, 25, 20, 10, 30)]
)
def test_parkings_anonymization_mgmt_cmd(batch, hours, result, permit_batch, permit_result, user_factory):
    user = user_factory()
    end_time = timezone.now() - datetime.timedelta(hours=hours)
    ArchivedParkingFactory.create_batch(batch, time_end=end_time)
    ParkingFactory.create_batch(batch, time_end=end_time)
    parking_checks = ParkingCheckFactory.create_batch(batch)

    for parking_check in parking_checks:
        parking_check.created_at = end_time
        parking_check.save(update_fields=["created_at"])

    expired_permit_list = create_permits(owner=user, count=permit_batch)
    for permit in expired_permit_list:
        subjects = permit.subjects
        for sub in subjects:
            sub["end_time"] = str(end_time)
            permit.save(update_fields=["subjects"])

    call_command(clean_reg_nums.Command())

    assert ParkingCheck.objects.filter(registration_number="").count() == result
    assert ArchivedParking.objects.filter(registration_number="").count() == result
    assert Parking.objects.filter(registration_number="").count() == result
    assert PermitLookupItem.objects.exclude(registration_number="").count() == permit_result
