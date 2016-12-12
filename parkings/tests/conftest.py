import pytest
from pytest_factoryboy import register

from parkings.factories import (
    AddressFactory, AdminUserFactory, OperatorFactory, ParkingFactory, StaffUserFactory, UserFactory
)

register(OperatorFactory)
register(ParkingFactory)
register(AdminUserFactory, 'admin_user')
register(StaffUserFactory, 'staff_user')
register(UserFactory)
register(AddressFactory)


@pytest.fixture(autouse=True)
def set_faker_random_seed():
    from parkings.factories.faker import fake
    fake.seed(777)
