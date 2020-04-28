import pytest
from rest_framework.test import APIClient

from .utils import token_authenticate


@pytest.fixture(autouse=True)
def no_more_mark_django_db(transactional_db):
    pass


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture()
def monitor(monitor_factory, user_factory):
    user = user_factory()
    return monitor_factory(user=user)


@pytest.fixture
def monitoring_api_client(monitor):
    api_client = APIClient()
    token_authenticate(api_client, monitor.user)
    api_client.monitor = monitor
    return api_client


@pytest.fixture
def user_api_client(user_factory):
    api_client = APIClient()
    user = user_factory()  # don't use the same user as operator_api_client
    token_authenticate(api_client, user)
    return api_client


@pytest.fixture
def staff_api_client(staff_user):
    api_client = APIClient()
    token_authenticate(api_client, staff_user)
    return api_client


@pytest.fixture()
def operator(operator_factory, user_factory):
    user = user_factory()
    return operator_factory(user=user)


@pytest.fixture
def operator_api_client(operator):
    api_client = APIClient()
    token_authenticate(api_client, operator.user)
    api_client.operator = operator
    return api_client


@pytest.fixture
def operator_2(operator, operator_factory):
    return operator_factory()


@pytest.fixture
def operator_2_api_client(operator_2):
    api_client = APIClient()
    token_authenticate(api_client, operator_2.user)
    api_client.operator = operator_2
    return api_client


@pytest.fixture()
def enforcer(enforcer_factory, user_factory):
    user = user_factory()
    return enforcer_factory(user=user)


@pytest.fixture
def enforcer_api_client(enforcer):
    api_client = APIClient()
    token_authenticate(api_client, enforcer.user)
    api_client.enforcer = enforcer
    return api_client
