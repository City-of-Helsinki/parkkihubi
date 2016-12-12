import factory
import pytz
from django.contrib.gis.geos import Point

from parkings.models import Parking

from .address import AddressFactory
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

    device_identifier = factory.LazyFunction(fake.uuid4)
    location = factory.LazyFunction(lambda: Point(60.1631665 + fake.random.uniform(0.001, 0.01),
                                                  24.9392813 + fake.random.uniform(0.001, 0.01)))
    operator = factory.SubFactory(OperatorFactory)
    registration_number = factory.LazyFunction(generate_registration_number)
    resident_code = factory.LazyFunction(lambda: fake.random.choice(CAPITAL_LETTERS))
    special_code = factory.LazyFunction(lambda: fake.random.choice(CAPITAL_LETTERS))
    time_start = factory.LazyFunction(lambda: fake.date_time_between(start_date='-2h', end_date='-1h', tzinfo=pytz.utc))
    time_end = factory.LazyFunction(lambda: fake.date_time_between(start_date='+1h', end_date='+2h', tzinfo=pytz.utc))
    zone = factory.LazyFunction(lambda: fake.random.randint(1, 3))
    address = factory.SubFactory(AddressFactory)
