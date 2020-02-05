import pytest
from django.core.exceptions import ValidationError
from django.utils import timezone

from ..factories.permit import (
    generate_areas, generate_external_ids, generate_subjects)
from ..models import Permit, PermitLookupItem


@pytest.mark.django_db
def test_permit_instance_creation_succeeds_with_valid_data(permit_series):
    permit_data = {
        'series': permit_series,
        'external_id': generate_external_ids(),
        'subjects': generate_subjects(count=1),
        'areas': generate_areas(count=1),
    }
    Permit.objects.create(**permit_data)
    instance = Permit.objects.first()

    assert Permit.objects.count() == 1
    assert PermitLookupItem.objects.count() == 1
    for key in permit_data.keys():
        assert getattr(instance, key) == permit_data[key]


@pytest.mark.django_db
def test_permit_instance_creation_errors_with_invalid_subjects(permit_series):
    subjects = generate_subjects()
    del subjects[0]['registration_number']
    permit_data = {
        'series': permit_series,
        'external_id': generate_external_ids(),
        'subjects': subjects,
        'areas': generate_areas(),
    }

    with pytest.raises(ValidationError):
        Permit.objects.create(**permit_data)
    assert Permit.objects.count() == 0


@pytest.mark.django_db
def test_permit_instance_creation_errors_with_invalid_areas(permit_series):
    areas = generate_areas()
    del areas[0]['start_time']
    permit_data = {
        'series': permit_series,
        'external_id': generate_external_ids(),
        'subjects': generate_subjects(),
        'areas': areas,
    }

    with pytest.raises(ValidationError):
        Permit.objects.create(**permit_data)
    assert Permit.objects.count() == 0


@pytest.mark.django_db
def test_permit_by_subject_manager_method(active_permit):
    registration_number = active_permit.subjects[0]['registration_number']

    filtered_permit_qs = Permit.objects.by_subject(registration_number)

    assert filtered_permit_qs.count() == 1
    permit = filtered_permit_qs.first()
    assert permit.subjects[0]['registration_number'] == registration_number


@pytest.mark.django_db
def test_permit_by_area_manager_method(active_permit):
    area = active_permit.areas[0]['area']

    filtered_permit_qs = Permit.objects.by_area(area)

    assert filtered_permit_qs.count() != 0
    for permit in filtered_permit_qs:
        assert any(area == _area['area'] for _area in permit.areas)
        assert not any(area + 'X' == _area['area'] for _area in permit.areas)


@pytest.mark.django_db
def test_permit_by_time_manager_method_invalid_time(active_permit):
    invalid_start_time = str(timezone.now() - timezone.timedelta(days=500))
    filtered_permit_qs = Permit.objects.by_time(invalid_start_time)

    assert filtered_permit_qs.count() == 0


@pytest.mark.django_db
def test_permit_by_time_manager_method_valid_time(active_permit):
    valid_start_time = active_permit.subjects[0]['start_time']
    filtered_permit_qs = Permit.objects.by_time(valid_start_time)

    assert filtered_permit_qs.count() == 1


@pytest.mark.django_db
def test_permitlookupitem_creation_ignored_for_start_date_gte_end_date(
        permit_series):
    areas = generate_areas()
    permit_data = {
        'series': permit_series,
        'external_id': generate_external_ids(),
        'subjects': [{
            'registration_number': 'ABC-123',
            'start_time': '2019-05-01T12:00:00+00:00',
            'end_time': '2019-05-01T11:55:00+00:00',
        }],
        'areas': [{
            'start_time': '2019-05-01T12:00:00+00:00',
            'end_time': '2019-05-30T12:00:00+00:00',
            'area': areas[0]['area'],
        }],
    }
    Permit.objects.create(**permit_data)

    assert Permit.objects.count() == 1
    assert PermitLookupItem.objects.count() == 0
