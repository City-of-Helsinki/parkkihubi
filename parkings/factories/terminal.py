import factory.django

from ..models import ParkingTerminal
from .faker import fake
from .gis import generate_location


class TerminalFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ParkingTerminal

    number = factory.Sequence(lambda n: 'T{}'.format(n + 1))
    name = factory.LazyFunction(fake.street_name)
    location = factory.LazyFunction(generate_location)
