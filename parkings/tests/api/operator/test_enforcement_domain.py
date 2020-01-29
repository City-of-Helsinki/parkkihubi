from django.urls import reverse
from rest_framework.status import HTTP_200_OK

list_url = reverse('operator:v1:enforcement_domain-list')


def test_enforcement_domain_list(operator_api_client, enforcement_domain):
    response = operator_api_client.get(list_url)
    json_response = response.json()

    assert response.status_code == HTTP_200_OK
    assert json_response['count'] == 1
    assert set(json_response['results'][0].keys()) == {'code', 'name'}
    assert json_response['results'][0]['code'] == enforcement_domain.code
    assert json_response['results'][0]['name'] == enforcement_domain.name
