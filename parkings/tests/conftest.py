import pytest
from pytest_factoryboy import register

from parkings.factories import (
    ActivePermitFactory, AdminUserFactory, DiscParkingFactory,
    EnforcementDomainFactory, EnforcerFactory, HistoryParkingFactory,
    OperatorFactory, ParkingAreaFactory, ParkingFactory, PermitFactory,
    PermitSeriesFactory, RegionFactory, StaffUserFactory, UserFactory)

register(OperatorFactory)
register(ParkingFactory, 'parking')
register(HistoryParkingFactory, 'history_parking')
register(AdminUserFactory, 'admin_user')
register(StaffUserFactory, 'staff_user')
register(UserFactory)
register(ParkingAreaFactory)
register(RegionFactory)
register(PermitFactory, 'permit')
register(PermitSeriesFactory, 'permit_series')
register(ActivePermitFactory, 'active_permit')
register(DiscParkingFactory, 'disc_parking')
register(EnforcementDomainFactory, 'enforcement_domain')
register(EnforcerFactory)


@pytest.fixture(autouse=True)
def set_faker_random_seed():
    from parkings.factories.faker import fake
    fake.seed(777)
