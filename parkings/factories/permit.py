# -*- coding: utf-8 -*-

import factory
import pytz

from parkings.models import Permit, PermitSeries

from .faker import fake
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


def generate_areas(count=1):
    areas = []
    for c in range(count):
        areas.append({
            'start_time': generate_timestamp_string('-2h', '-1h'),
            'end_time': generate_timestamp_string('+1h', '+2h'),
            'area': fake.random.choice(CAPITAL_LETTERS),
        })
    return areas


def generate_external_ids(id_length=11):
    external_id = ''.join(fake.random.choice('0123456789') for _ in range(id_length))
    return external_id


class PermitSeriesFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = PermitSeries
    owner = factory.SubFactory(UserFactory)


class PermitFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Permit

    series = factory.SubFactory(PermitSeriesFactory)
    external_id = factory.LazyFunction(lambda: generate_external_ids())
    subjects = factory.LazyFunction(lambda: generate_subjects(count=2))
    areas = factory.LazyFunction(lambda: generate_areas(count=3))


class ActivePermitFactory(PermitFactory):
    series = factory.LazyFunction(lambda: PermitSeriesFactory(active=True))
