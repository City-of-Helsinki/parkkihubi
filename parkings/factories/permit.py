# -*- coding: utf-8 -*-

import pytz
from django.contrib.auth import get_user_model

from parkings.models import EnforcementDomain, Permit, PermitArea, PermitSeries

from .faker import fake
from .gis import generate_multi_polygon
from .user import UserFactory

CAPITAL_LETTERS = 'ABCDEFGHIJKLMNOPQRSTUVWXYZÅÄÖ'


def generate_registration_number():
    letters = ''.join(fake.random.choice(CAPITAL_LETTERS) for _ in range(3))
    numbers = ''.join(fake.random.choice('0123456789') for _ in range(3))
    return '%s-%s' % (letters, numbers)


def generate_timestamp_string(start, end):
    dt = fake.date_time_between(
        start_date=start, end_date=end, tzinfo=pytz.utc)
    return '{}'.format(dt).replace(' ', 'T')


def generate_subjects(count=1):
    subjects = []
    for c in range(count):
        subjects.append({
            'registration_number': generate_registration_number(),
            'start_time': generate_timestamp_string('-2h', '-1h'),
            'end_time': generate_timestamp_string('+1h', '+2h'),
        })
    return subjects


def create_permit_area(identifier, domain=None, allowed_user=None):
    geom = generate_multi_polygon()
    if allowed_user is None:
        allowed_user = get_user_model().objects.get_or_create(
            username='TEST_STAFF',
            defaults={'is_staff': True}
        )[0]
    if domain is None:
        domain = EnforcementDomain.get_default_domain()
    (area, created) = PermitArea.objects.get_or_create(
        identifier=identifier,
        domain=domain,
        defaults={
            'name': "Kamppi",
            'geom': geom,
        }
    )
    if created:
        area.allowed_users.add(allowed_user)


def generate_areas(domain=None, count=1, allowed_user=None):
    areas = []
    for c in range(count):
        identifier = fake.random.choice(CAPITAL_LETTERS)
        areas.append({
            'start_time': generate_timestamp_string('-2h', '-1h'),
            'end_time': generate_timestamp_string('+1h', '+2h'),
            'area': identifier,
        })
        create_permit_area(identifier, domain, allowed_user)
    return areas


def generate_external_ids(id_length=11):
    external_id = ''.join(fake.random.choice('0123456789') for _ in range(id_length))
    return external_id


def create_permits(active=False, owner=None, domain=None, count=3):
    series = create_permit_series(active=active, owner=owner)
    return [
        create_permit(domain=domain, series=series, owner=owner)
        for _ in range(count)
    ]


def create_permit_series(active=False, owner=None):
    return PermitSeries.objects.create(
        active=active,
        owner=owner or UserFactory(),
    )


def create_permit(
        domain=None,
        series=None,
        external_id=None,
        owner=None,
        active=False,
        subject_count=2,
        area_count=3,
):
    domain = domain or EnforcementDomain.objects.get_or_create(
        code='TESTDOM', defaults={'name': 'Test domain'})[0]
    owner = owner or get_user_model().objects.get_or_create(
        username='TEST_STAFF',
        defaults={'is_staff': True}
    )[0]
    series = series or create_permit_series(active=active, owner=owner)
    return Permit.objects.get_or_create(
        domain=domain,
        series=series,
        external_id=external_id,
        subjects=generate_subjects(count=subject_count),
        areas=generate_areas(
            domain=domain,
            count=area_count,
            allowed_user=owner,
        ),
    )[0]
