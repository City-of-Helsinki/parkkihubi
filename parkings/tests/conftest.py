import pytest
from pytest_factoryboy import register

from parkings.factories import AdminUserFactory, OperatorFactory, ParkingFactory, StaffUserFactory, UserFactory

register(OperatorFactory)
register(ParkingFactory)
register(AdminUserFactory, 'admin_user')
register(StaffUserFactory, 'staff_user')
register(UserFactory)


@pytest.fixture(autouse=True)
def set_faker_random_seed():
    from parkings.factories.faker import fake
    fake.seed(777)
