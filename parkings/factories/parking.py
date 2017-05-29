from datetime import timedelta

import factory
import pytz
from django.conf import settings
from django.contrib.gis.geos import Point

from parkings.models import Parking

from .faker import fake
from .operator import OperatorFactory

CAPITAL_LETTERS = 'ABCDEFGHIJKLMNOPQRSTUVWXYZÅÄÖ'


def generate_registration_number():
    letters = ''.join(fake.random.choice(CAPITAL_LETTERS) for _ in range(3))
    numbers = ''.join(fake.random.choice('0123456789') for _ in range(3))
    return '%s-%s' % (letters, numbers)


class ParkingFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Parking

    location = factory.LazyFunction(
        lambda: Point(24.915 + fake.random.uniform(0, 0.040), 60.154 + fake.random.uniform(0, 0.022))
    )
    operator = factory.SubFactory(OperatorFactory)
    registration_number = factory.LazyFunction(generate_registration_number)
    time_start = factory.LazyFunction(lambda: fake.date_time_between(start_date='-2h', end_date='-1h', tzinfo=pytz.utc))
    time_end = factory.LazyFunction(lambda: fake.date_time_between(start_date='+1h', end_date='+2h', tzinfo=pytz.utc))
    zone = factory.LazyFunction(lambda: fake.random.randint(1, 3))


class HistoryParkingFactory(ParkingFactory):
    time_end = factory.LazyFunction(
        lambda: (
            fake.date_time_this_decade(before_now=True, tzinfo=pytz.utc) -
            getattr(settings, 'PARKKIHUBI_TIME_PARKINGS_HIDDEN', timedelta(days=7))
        )
    )
    time_start = factory.lazy_attribute(lambda o: o.time_end - timedelta(seconds=fake.random.randint(0, 60*24*14)))
