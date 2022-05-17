import datetime

import pytest
from django.core.management import call_command
from django.utils import timezone

from parkings.anonymization import (
    anonymize_archived_parking_registration_numbers,
    anonymize_parking_check_registration_numbers,
    anonymize_parking_registration_numbers,
    anonymize_permit_registration_numbers)
from parkings.factories import (
    ArchivedParkingFactory, ParkingCheckFactory, ParkingFactory)
from parkings.factories.permit import create_permits
from parkings.management.commands import clean_reg_nums
from parkings.models import (
    ArchivedParking, Parking, ParkingCheck, PermitLookupItem)


@pytest.mark.django_db
@pytest.mark.parametrize('batch, hours, result', [(10, 2, 0), (20, 25, 20)])
def test_anonymization_of_archived_parkings_registration_number(batch, hours, result):
    end_time = timezone.now() - datetime.timedelta(hours=hours)
    ArchivedParkingFactory.create_batch(batch, time_end=end_time)

    anonymize_archived_parking_registration_numbers()

    assert ArchivedParking.objects.filter(registration_number="").count() == result


@pytest.mark.django_db
@pytest.mark.parametrize('batch, hours, result', [(10, 2, 0), (20, 25, 20)])
def test_anonymization_of_parkings_registration_number(batch, hours, result):
    end_time = timezone.now() - datetime.timedelta(hours=hours)
    ParkingFactory.create_batch(batch, time_end=end_time)

    anonymize_parking_registration_numbers()

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

    anonymize_parking_check_registration_numbers()
    assert ParkingCheck.objects.filter(registration_number="").count() == result


@pytest.fixture
def test_anonymization_of_permit_registration_number_for_expired_permits(user_factory):
    user = user_factory()
    expired_permit_list = create_permits(owner=user, count=5)
    past_time = timezone.now() - datetime.timedelta(hours=25)
    for permit in expired_permit_list:
        subjects = permit.subjects
        for sub in subjects:
            sub["end_time"] = past_time
            permit.subjects = subjects
            permit.save(update_fields=["subjects"])

    anonymize_permit_registration_numbers()
    assert PermitLookupItem.objects.filter(registration_number="").count() == 5


@pytest.fixture
def test_anonymization_of_permit_registration_number_should_not_happen_for_valid_permits(user_factory):
    user = user_factory()
    create_permits(owner=user, count=3)

    anonymize_permit_registration_numbers()
    assert PermitLookupItem.objects.exclude(registration_number="").count() == 3


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
