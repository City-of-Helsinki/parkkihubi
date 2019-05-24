import pytest
from django.core.exceptions import ValidationError
from django.utils import timezone

from ..models import Parking, Permit, PermitCacheItem
from .utils import (
    generate_areas, generate_areas_with_startdate_gt_endate,
    generate_external_ids, generate_subjects,
    generate_subjects_with_startdate_gt_endate)


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
    assert PermitCacheItem.objects.count() == 1
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
    normalized_reg_num = Parking.normalize_reg_num(registration_number)

    filtered_permit_qs = Permit.objects.by_subject(normalized_reg_num)

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

    assert filtered_permit_qs.count() != 0
    assert filtered_permit_qs.count() == PermitCacheItem.objects.filter(start_time__lte=valid_start_time).count()


@pytest.mark.django_db
def test_permitcacheitem_creation_ignored_for_start_date_gte_end_date(permit_series):
    permit_data = {
        'series': permit_series,
        'external_id': generate_external_ids(),
        'subjects': generate_subjects_with_startdate_gt_endate(),
        'areas': generate_areas_with_startdate_gt_endate(),
    }
    Permit.objects.create(**permit_data)

    assert Permit.objects.count() == 1
    assert PermitCacheItem.objects.count() == 0
