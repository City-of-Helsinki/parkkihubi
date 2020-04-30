from django.urls import reverse
from rest_framework.status import HTTP_200_OK

from parkings.factories import EnforcerFactory
from parkings.models import PaymentZone

from ..enforcement.test_check_parking import create_area_geom

list_url = reverse("operator:v1:paymentzone-list")


def test_endpoint_returns_paymentzone_list(operator_api_client, operator):
    enforcer = EnforcerFactory(user=operator.user)

    zone = PaymentZone.objects.create(
        domain=enforcer.enforced_domain,
        code="1",
        name="Maksuvyöhyke 1",
        number=1,
        geom=create_area_geom(),
    )

    response = operator_api_client.get(list_url)
    json_response = response.json()

    assert response.status_code == HTTP_200_OK
    assert json_response["count"] == 1
    expected_keys = {"domain", "code", "name"}
    assert set(json_response["results"][0]) == expected_keys
    assert json_response["results"][0]["domain"] == zone.domain.code
    assert json_response["results"][0]["code"] == "1"
    assert json_response["results"][0]["name"] == "Maksuvyöhyke 1"


def test_endpoint_returns_all_paymentzones(
        operator_api_client, operator, staff_user):
    enforcer = EnforcerFactory(user=staff_user)
    domain = enforcer.enforced_domain
    assert not hasattr(operator_api_client.auth_user, 'enforcer')

    PaymentZone.objects.create(
        domain=domain,
        code="1",
        name="Maksuvyöhyke 1",
        number=1,
        geom=create_area_geom(),
    )

    PaymentZone.objects.create(
        domain=domain,
        code="2",
        name="Maksuvyöhyke 2",
        number=2,
        geom=create_area_geom(),
    )

    response = operator_api_client.get(list_url)

    json_response = response.json()
    assert response.status_code == HTTP_200_OK
    assert json_response["count"] == 2
    assert json_response["results"] == [
        {'code': '1', 'domain': domain.code, 'name': 'Maksuvyöhyke 1'},
        {'code': '2', 'domain': domain.code, 'name': 'Maksuvyöhyke 2'},
    ]
    assert PaymentZone.objects.count() == 2
