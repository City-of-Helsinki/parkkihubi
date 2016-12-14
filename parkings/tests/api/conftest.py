import pytest
from rest_framework.test import APIClient

from .utils import token_authenticate


@pytest.fixture(autouse=True)
def no_more_mark_django_db(transactional_db):
    pass


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def user_api_client(api_client, user_factory):
    user = user_factory()  # don't use the same user as operator_api_client
    token_authenticate(api_client, user)
    return api_client


@pytest.fixture
def staff_api_client(api_client, staff_user):
    token_authenticate(api_client, staff_user)
    return api_client


@pytest.fixture
def admin_api_client(api_client, admin_user):
    token_authenticate(api_client, admin_user)
    return api_client


@pytest.fixture
def operator_api_client(api_client, operator):
    token_authenticate(api_client, operator.user)
    return api_client


@pytest.fixture
def operator_2(operator, operator_factory):
    return operator_factory()


@pytest.fixture
def operator_2_api_client(api_client, operator, operator_2):
    token_authenticate(api_client, operator_2.user)
    return api_client
