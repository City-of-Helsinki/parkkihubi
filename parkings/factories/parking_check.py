# -*- coding: utf-8 -*-

import factory
import pytz
from django.contrib.gis.geos import Point

from parkings.models.parking_check import ParkingCheck

from .faker import fake
from .user import UserFactory

CAPITAL_LETTERS = 'ABCDEFGHIJKLMNOPQRSTUVWXYZÅÄÖ'


def generate_registration_number():
    letters = ''.join(fake.random.choice(CAPITAL_LETTERS) for _ in range(3))
    numbers = ''.join(fake.random.choice('0123456789') for _ in range(3))
    return '%s-%s' % (letters, numbers)


class ParkingCheckFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ParkingCheck
    registration_number = factory.LazyFunction(generate_registration_number)
    time = factory.LazyFunction(lambda: fake.date_time_this_decade(before_now=True, tzinfo=pytz.utc))
    allowed = True
    found_parking = None
    time_overridden = True
    result = {
        'location': {
            'payment_zone': fake.random.choice('0123456789'),
            'permit_area': fake.random.choice(CAPITAL_LETTERS)
        }
    }
    performer = factory.SubFactory(UserFactory)
    location = factory.LazyFunction(
        lambda: Point(24.915 + fake.random.uniform(0, 0.040), 60.154 + fake.random.uniform(0, 0.022))
    )
