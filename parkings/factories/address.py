import factory

from parkings.models import Address

from .faker import fake


class AddressFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Address

    city = factory.LazyFunction(fake.city_name)
    postal_code = factory.LazyFunction(fake.postcode)
    street = factory.LazyFunction(fake.street_address)
