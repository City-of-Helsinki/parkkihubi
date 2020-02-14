from django.urls import reverse
from rest_framework.status import (
    HTTP_200_OK, HTTP_201_CREATED, HTTP_204_NO_CONTENT, HTTP_404_NOT_FOUND)

from parkings.models import EnforcementDomain, Enforcer, Permit

from ....factories.permit import (
    generate_areas, generate_external_ids, generate_subjects)

list_url = reverse('operator:v1:permit-list')


def _get_detail_url(obj):
    return reverse('operator:v1:permit-detail', kwargs={'pk': obj.pk})


def _get_permit_data(permit_series):
    return {
        'series': permit_series.id,
        'external_id': generate_external_ids(),
        'subjects': generate_subjects(),
        'areas': generate_areas(),
    }


def _check_response(data, obj):
    permit_response_keys = {
        'series',
        'domain',
        'external_id',
        'id',
        'subjects',
        'areas',
    }

    assert set(data.keys()) == permit_response_keys
    assert obj.series.pk == data['series']
    assert obj.domain.code == data['domain']
    assert obj.external_id == data['external_id']
    assert obj.id == data['id']
    assert obj.subjects == data['subjects']
    assert obj.areas == data['areas']


def _create_enforcement_domain_and_enforcer(user, code='ESP'):
    domain = EnforcementDomain.objects.create(code=code, name='EspooDomain')
    enforcer = Enforcer.objects.create(user=user, enforced_domain=domain)

    return (domain, enforcer)


def test_operator_can_create_permit_with_valid_post_data(
    operator_api_client, permit_series, operator
):
    domain, _ = _create_enforcement_domain_and_enforcer(operator.user)
    permit_data = _get_permit_data(permit_series)
    permit_data.update(domain=domain.code)

    response = operator_api_client.post(list_url, data=permit_data)

    assert response.status_code == HTTP_201_CREATED
    _check_response(response.json(), Permit.objects.first())


def test_operator_cannot_view_permit_owned_by_other_operator(
    operator_api_client, operator_2_api_client, operator,
    operator_2, permit_series_factory, permit_factory,
):
    operator1_owned_permitseries = permit_series_factory(owner=operator.user)
    operator2_owned_permitseries = permit_series_factory(owner=operator_2.user)

    operator1_permit_list = [permit_factory(series=operator1_owned_permitseries) for _ in range(3)]
    operator2_permit_list = [permit_factory(series=operator2_owned_permitseries) for _ in range(3)]

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
    permit_series_factory, permit_factory
):
    operator1_owned_permitseries = permit_series_factory(owner=operator.user)
    operator2_owned_permitseries = permit_series_factory(owner=operator_2.user)

    operator1_permit_list = [permit_factory(series=operator1_owned_permitseries) for _ in range(3)]
    operator2_permit_list = [permit_factory(series=operator2_owned_permitseries) for _ in range(3)]

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
    permit_series_factory, permit_factory
):
    operator1_owned_permitseries = permit_series_factory(owner=operator.user)
    operator2_owned_permitseries = permit_series_factory(owner=operator_2.user)

    operator1_permit_list = [permit_factory(series=operator1_owned_permitseries) for _ in range(3)]
    operator2_permit_list = [permit_factory(series=operator2_owned_permitseries) for _ in range(3)]

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
    operator_api_client, permit_series_factory, operator, staff_api_client,
    staff_user, permit_factory
):
    reg_number = 'ABC-123'
    permit_subject = generate_subjects()
    permit_subject[0].update(registration_number=reg_number)

    enforcer_domain = EnforcementDomain.objects.create(code='HEL', name='HelDomain')
    enforcer_permitseries = permit_series_factory(owner=staff_user)
    enforcer_permit_list = [
        permit_factory(subjects=permit_subject, series=enforcer_permitseries, domain=enforcer_domain)
        for _
        in range(3)
    ]
    Enforcer.objects.create(user=staff_user, enforced_domain=enforcer_domain)

    operator_domain = EnforcementDomain.objects.create(code='ESP', name='EspooDomain')
    operator_permitseries = permit_series_factory(owner=operator.user)
    operator_permit_domain = [operator_domain, enforcer_domain]
    operator_permit_list = [
        permit_factory(subjects=permit_subject, domain=domain, series=operator_permitseries)
        for domain
        in operator_permit_domain
        ]

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
    response = staff_api_client.get(enforcement_permit_url)
    json_response = response.json()

    assert response.status_code == HTTP_200_OK
    assert json_response['count'] == 3
    assert set([permit['id'] for permit in json_response['results']]) == set(
        [permit.id for permit in enforcer_permit_list]
    )
