import factory

from parkings.factories import EnforcementDomainFactory
from parkings.models import Monitor

from .faker import fake
from .user import UserFactory


class MonitorFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Monitor

    name = factory.LazyFunction(fake.company)
    user = factory.SubFactory(UserFactory)
    domain = factory.SubFactory(EnforcementDomainFactory)
