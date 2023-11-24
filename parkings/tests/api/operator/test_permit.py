import pytest
from django.urls import reverse
from rest_framework.status import (
    HTTP_200_OK, HTTP_201_CREATED, HTTP_204_NO_CONTENT, HTTP_400_BAD_REQUEST,
    HTTP_404_NOT_FOUND)

from parkings.models import EnforcementDomain, Permit, PermitArea

from ....factories.permit import (
    create_permit_series, create_permits, generate_areas,
    generate_external_ids, generate_subjects)
from ..enforcement.test_check_parking import create_area_geom

list_url = reverse('operator:v1:permit-list')


def _get_detail_url(obj):
    return reverse('operator:v1:permit-detail', kwargs={'pk': obj.pk})


def _check_response(data, obj):
    permit_response_keys = {
        'series',
        'domain',
        'external_id',
        'id',
        'subjects',
        'areas',
        'properties',
    }

    assert set(data.keys()) == permit_response_keys
    assert obj.series.pk == data['series']
    assert obj.domain.code == data['domain']
    assert obj.external_id == data['external_id']
    assert obj.id == data['id']
    assert obj.subjects == data['subjects']
    assert obj.areas == data['areas']


def test_operator_can_create_permit_with_valid_post_data(
    operator_api_client, operator
):
    domain = EnforcementDomain.objects.get_or_create(
        code='TSTDOM', defaults={'name': 'Test domain'})[0]
    permit_data = {
        'series': create_permit_series(owner=operator.user).id,
        'external_id': generate_external_ids(),
        'domain': 'TSTDOM',
        'subjects': generate_subjects(),
        'areas': generate_areas(domain, allowed_user=operator.user),
    }

    response = operator_api_client.post(list_url, data=permit_data)

    assert response.status_code == HTTP_201_CREATED
    _check_response(response.json(), Permit.objects.first())


def test_operator_cannot_view_permit_owned_by_other_operator(
    operator_api_client, operator_2_api_client, operator, operator_2,
):
    operator1_permit_list = create_permits(owner=operator.user, count=3)
    operator2_permit_list = create_permits(owner=operator_2.user, count=3)

    response = operator_api_client.get(list_url)
    json_response = response.json()

    assert response.status_code == HTTP_200_OK
    assert json_response['count'] == 3
    assert Permit.objects.count() == 6
    assert set([permit['id'] for permit in json_response['results']]) == set(
        [permit.id for permit in operator1_permit_list]
    )

    operator_permit_response_obj = [
        permit
        for permit in json_response['results']
        if permit['id'] == operator1_permit_list[0].id
    ][0]
    _check_response(operator_permit_response_obj, operator1_permit_list[0])

    response = operator_2_api_client.get(list_url)
    json_response = response.json()

    assert response.status_code == HTTP_200_OK
    assert json_response['count'] == 3
    assert set([permit['id'] for permit in json_response['results']]) == set(
        [permit.id for permit in operator2_permit_list]
    )

    operator2_permit_response_obj = [
        permit
        for permit in json_response['results']
        if permit['id'] == operator2_permit_list[0].id
    ][0]
    _check_response(operator2_permit_response_obj, operator2_permit_list[0])


def test_operator_cannot_modify_permit_owned_by_other_operator(
    operator_api_client, operator, operator_2,
):
    operator1_permit_list = create_permits(owner=operator.user, count=3)
    operator2_permit_list = create_permits(owner=operator_2.user, count=3)

    operator1_permit = operator1_permit_list[0]
    operator2_permit = operator2_permit_list[0]
    patch_data = {'external_id': 'ABC123'}

    response = operator_api_client.patch(
        _get_detail_url(operator2_permit), data=patch_data
    )

    assert response.status_code == HTTP_404_NOT_FOUND

    response = operator_api_client.patch(
        _get_detail_url(operator1_permit), data=patch_data
    )

    assert response.status_code == HTTP_200_OK
    assert response.json()['external_id'] == 'ABC123'


def test_operator_cannot_delete_permit_owned_by_other_operator(
    operator_api_client, operator, operator_2,
):
    operator1_permit_list = create_permits(owner=operator.user, count=3)
    operator2_permit_list = create_permits(owner=operator_2.user, count=3)

    operator1_permit = operator1_permit_list[0]
    operator2_permit = operator2_permit_list[0]

    response = operator_api_client.delete(
        _get_detail_url(operator2_permit)
    )

    assert response.status_code == HTTP_404_NOT_FOUND
    assert Permit.objects.count() == 6

    response = operator_api_client.delete(
        _get_detail_url(operator1_permit)
    )

    assert response.status_code == HTTP_204_NO_CONTENT
    assert Permit.objects.count() == 5
    assert not Permit.objects.filter(id=operator1_permit.id).exists()


def test_operator_and_enforcers_cannot_see_each_others_permit(
    operator_api_client, operator, enforcer_api_client, staff_user,
):
    reg_number = 'ABC-123'
    permit_subject = generate_subjects()
    permit_subject[0].update(registration_number=reg_number)

    enforcer = enforcer_api_client.enforcer
    domain = enforcer.enforced_domain

    enforcer_permit_list = create_permits(
        owner=enforcer.user, domain=domain, count=3)

    operator_permit_list = create_permits(
        owner=operator.user, domain=domain, count=2)

    #  Operator should see only operator_permit_list
    response = operator_api_client.get(list_url)
    json_response = response.json()

    assert response.status_code == HTTP_200_OK
    assert json_response['count'] == 2
    assert set([permit['id'] for permit in json_response['results']]) == set(
        [permit.id for permit in operator_permit_list]
    )

    enforcement_permit_url = reverse('enforcement:v1:permit-list')

    #  Enforcer should see only enforcer_permit_list
    response = enforcer_api_client.get(enforcement_permit_url)
    json_response = response.json()

    assert response.status_code == HTTP_200_OK
    assert json_response['count'] == 3
    assert set([permit['id'] for permit in json_response['results']]) == set(
        [permit.id for permit in enforcer_permit_list]
    )


@pytest.mark.parametrize('allowed', ['allowed', 'denied'])
@pytest.mark.parametrize('number_of_allowed_users', [1, 2])
@pytest.mark.parametrize('mode', ['single', 'bulk'])
def test_area_restriction(
    allowed,
    number_of_allowed_users,
    mode,
    operator_api_client,
    operator,
    staff_user,
    enforcer,
):
    area = {
        'start_time': '2020-01-01T00:00:00+00:00',
        'end_time': '2020-12-31T23:59:59+00:00',
        'area': 'AR3A',
    }

    permit_series = create_permit_series(active=True, owner=operator.user)
    domain = EnforcementDomain.objects.create(code='HKI', name='Helsinki')

    permit_data = {
        'series': permit_series.id,
        'external_id': 'EXT-id-123',
        'subjects': generate_subjects(),
        'areas': [area],
        'domain': 'HKI',
        'properties': {'permit_type': 'Asukaspysäköintitunnus'},
    }

    permit_area = PermitArea.objects.create(
        name='Kamppi',
        identifier='AR3A',
        geom=create_area_geom(),
        domain=domain,
    )
    if number_of_allowed_users == 2:
        permit_area.allowed_users.add(enforcer.user)
    if allowed == "allowed":
        permit_area.allowed_users.add(operator.user)
    else:
        permit_area.allowed_users.add(staff_user)

    data = permit_data if mode == 'single' else [permit_data]

    response = operator_api_client.post(list_url, data=data)

    response_item = response.json() if mode == 'single' else response.json()[0]

    if allowed == 'allowed':
        returned_id = response_item.pop('id', None)
        assert response_item == permit_data
        assert response.status_code == HTTP_201_CREATED
        assert isinstance(returned_id, int)
    else:
        assert response_item == {'areas': ['Unknown identifiers: AR3A']}
        assert response.status_code == HTTP_400_BAD_REQUEST
