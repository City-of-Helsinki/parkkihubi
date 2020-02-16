import factory

from parkings.models import EnforcementDomain, Enforcer

from .faker import fake
from .user import UserFactory


class EnforcementDomainFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = EnforcementDomain

    name = factory.LazyFunction(fake.city)
    code = factory.Sequence(lambda n: 'DMN%d' % (n + 1))


class EnforcerFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Enforcer

    name = factory.LazyFunction(fake.name)
    user = factory.SubFactory(UserFactory)
    enforced_domain = factory.SubFactory(EnforcementDomainFactory)
