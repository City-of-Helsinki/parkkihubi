import pytest
from pytest_factoryboy import register

from parkings.factories import (
    AdminUserFactory, HistoryParkingFactory, OperatorFactory,
    ParkingAreaFactory, ParkingFactory, RegionFactory, StaffUserFactory,
    UserFactory)

register(OperatorFactory)
register(ParkingFactory, 'parking')
register(HistoryParkingFactory, 'history_parking')
register(AdminUserFactory, 'admin_user')
register(StaffUserFactory, 'staff_user')
register(UserFactory)
register(ParkingAreaFactory)
register(RegionFactory)


@pytest.fixture(autouse=True)
def set_faker_random_seed():
    from parkings.factories.faker import fake
    fake.seed(777)
