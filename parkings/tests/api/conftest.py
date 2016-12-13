import pytest
from rest_framework.test import APIClient


@pytest.fixture(autouse=True)
def no_more_mark_django_db(transactional_db):
    pass


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def user_api_client(api_client, user):
    api_client.force_authenticate(user)
    return api_client


@pytest.fixture
def staff_api_client(api_client, staff_user):
    api_client.force_authenticate(staff_user)
    return api_client


@pytest.fixture
def admin_api_client(api_client, admin_user):
    api_client.force_authenticate(admin_user)
    return api_client


@pytest.fixture
def operator_api_client(api_client, operator):
    api_client.force_authenticate(operator.user)
    return api_client
