import factory

from parkings.factories import EnforcementDomainFactory
from parkings.models import Region

from .faker import fake
from .gis import generate_multi_polygon


class RegionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Region

    geom = factory.LazyFunction(generate_multi_polygon)
    capacity_estimate = factory.LazyFunction(lambda: fake.random.randint(0, 500))
    name = factory.LazyFunction(fake.city)
    domain = factory.SubFactory(EnforcementDomainFactory)
