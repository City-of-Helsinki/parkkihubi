import factory

from parkings.models import Operator

from .faker import fake
from .user import UserFactory


class OperatorFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Operator

    name = factory.LazyFunction(fake.company)
    user = factory.SubFactory(UserFactory)
