import pytest
from django.urls import reverse
from rest_framework.status import (
    HTTP_200_OK, HTTP_201_CREATED, HTTP_400_BAD_REQUEST, HTTP_403_FORBIDDEN)

from ....factories.permit import (
    create_permit_area, create_permit_series, create_permits, generate_areas,
    generate_external_ids, generate_subjects)
from ....models import (
    EnforcementDomain, Permit, PermitLookupItem, PermitSeries)

list_url = reverse('enforcement:v1:permit-list')


def generate_areas_data(client):
    return generate_areas(
        domain=client.enforcer.enforced_domain,
        allowed_user=client.auth_user)


@pytest.mark.parametrize(
    'user_api',
    ['anonymous_user', 'operator', 'staff']
)
@pytest.mark.django_db
def test_unauthorized_user_cannot_create_permit(
    user_api_client, operator_api_client, staff_api_client, user_api
):
    if user_api == 'anonymous_user':
        client = user_api_client
    elif user_api == 'operator':
        client = operator_api_client
    else:
        client = staff_api_client
    permit_data = {
        'series': create_permit_series(owner=client.auth_user).id,
        'external_id': generate_external_ids(),
        'subjects': generate_subjects(),
        'areas': generate_areas(),
    }

    response = client.post(list_url, data=permit_data)

    assert response.status_code == HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_permit_is_created_with_valid_post_data(enforcer_api_client):
    permit_data = {
        'series': create_permit_series(owner=enforcer_api_client.auth_user).id,
        'external_id': generate_external_ids(),
        'subjects': generate_subjects(),
        'areas': generate_areas_data(enforcer_api_client),
    }

    response = enforcer_api_client.post(list_url, data=permit_data)

    assert response.status_code == HTTP_201_CREATED


def test_cannot_override_domain(enforcer_api_client):
    domain = EnforcementDomain.objects.get_or_create(
        code='FOODOMAIN', defaults={'name': 'Foo'})[0]
    permit_data = {
        'domain': 'FOODOMAIN',
        'series': create_permit_series(owner=enforcer_api_client.auth_user).id,
        'external_id': generate_external_ids(),
        'subjects': generate_subjects(),
        'areas': generate_areas(domain=domain),
    }

    response = enforcer_api_client.post(list_url, data=permit_data)

    assert response.json() == {'domain': ['Not allowed']}
    assert response.status_code == HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_permit_is_not_created_to_non_owned_series(enforcer_api_client):
    series = create_permit_series()
    assert series.owner != enforcer_api_client.auth_user
    permit_data = {
        'series': series.id,
        'external_id': generate_external_ids(),
        'subjects': generate_subjects(),
        'areas': generate_areas_data(enforcer_api_client),
    }

    response = enforcer_api_client.post(list_url, data=permit_data)

    assert response.json() == {
        'series': [
            'Invalid pk "{}" - object does not exist.'.format(series.pk)
        ],
    }
    assert response.status_code == HTTP_400_BAD_REQUEST
    assert Permit.objects.count() == 0


@pytest.mark.django_db
def test_permit_is_created_with_empty_lists(enforcer_api_client):
    permit_data = {
        'series': create_permit_series(owner=enforcer_api_client.auth_user).id,
        'external_id': "E-123",
        'subjects': [],
        'areas': [],
    }

    response = enforcer_api_client.post(list_url, data=permit_data)

    assert response.status_code == HTTP_201_CREATED


TS1 = '2019-01-01T12:00:00Z'
TS2 = '2019-06-30T12:00:00Z'
INVALID_DATA_TEST_CASES = {
    'non-list': (
        {'foo': 'bar'},
        'Must be a list'),
    'item-not-dict': (
        [123, 456, 789],
        'Each list item must be a dictionary'),
    'invalid-field': (
        [{'start_time': 1, 'end_time': 2, 'registration_number': 3, 'foo': 4}],
        'Unknown fields in item: foo'),
    'missing-regnum': (
        [{'start_time': TS1, 'end_time': TS2}],
        'Field "registration_number" is missing from an item'),
    'non-string-regnum': (
        [{'start_time': TS1, 'end_time': TS2, 'registration_number': 666}],
        'Invalid "registration_number" value 666: Not a string'),
    'too-long-regnum': (
        [{'start_time': TS1, 'end_time': TS2,
          'registration_number': 21 * 'A'}],
        'Invalid "registration_number" value \'AAAAAAAAAAAAAAAAAAAAA\':'
        ' Value longer than 20 characters'),
    'missing-endtime': (
        [{'start_time': TS1, 'registration_number': 'X-14'}],
        'Field "end_time" is missing from an item'),
    'non-string-timestamp': (
        [{'start_time': TS1, 'end_time': 2019, 'registration_number': 'X-14'}],
        'Invalid "end_time" value 2019: Not a string'),
    'invalid-timestamp': (
        [{'start_time': TS1, 'end_time': '', 'registration_number': 'X-14'}],
        'Invalid "end_time" value \'\': Not a timestamp string'),
    'no-timezone': (
        [{'start_time': TS1, 'end_time': '2019-12-31T00:00:00',
          'registration_number': 'X-14'}],
        'Invalid "end_time" value \'2019-12-31T00:00:00\': Missing timezone'),
}


@pytest.mark.parametrize('kind', ['single', 'bulk'])
@pytest.mark.parametrize('test_case', INVALID_DATA_TEST_CASES.keys())
@pytest.mark.django_db
def test_permit_is_not_created_with_invalid_post_data(
        enforcer_api_client, kind, test_case):
    (subjects, error) = INVALID_DATA_TEST_CASES[test_case]
    invalid_permit_data = {
        'series': create_permit_series(owner=enforcer_api_client.auth_user).id,
        'external_id': 'EXT-1',
        'subjects': subjects,
        'areas': generate_areas_data(enforcer_api_client),
    }

    if kind == 'single':
        response = enforcer_api_client.post(list_url, data=invalid_permit_data)
        data = response.data
    else:
        response = enforcer_api_client.post(list_url, data=[invalid_permit_data])
        data = response.data[0]

    assert response.status_code == HTTP_400_BAD_REQUEST
    assert data['subjects'] == [error]


@pytest.mark.parametrize('kind', ['single', 'bulk'])
@pytest.mark.parametrize('input_timestamp,normalized_timestamp', [
    ('1995-01-01 12:00Z', '1995-01-01T12:00:00+00:00'),
    ('2030-06-30T12:00+03:00', '2030-06-30T09:00:00+00:00'),
    ('1995-01-01 12:00:00 UTC', '1995-01-01T12:00:00+00:00'),
    ('2019-05-30T12:00:00.123Z', '2019-05-30T12:00:00.123000+00:00'),
    ('2019-05-30T12:00:00.999999 +00:00', '2019-05-30T12:00:00.999999+00:00'),
])
@pytest.mark.django_db
def test_permit_creation_normalizes_timestamps(
        enforcer_api_client,
        kind,
        input_timestamp, normalized_timestamp):
    domain = enforcer_api_client.enforcer.enforced_domain
    user = enforcer_api_client.auth_user
    area_identifier = 'area name'
    create_permit_area(area_identifier, domain=domain, allowed_user=user)
    permit_data = {
        'series': create_permit_series(owner=enforcer_api_client.auth_user).id,
        'external_id': 'E123',
        'subjects': [{
            'start_time': '1970-01-01T00:00:00+00:00',
            'end_time': input_timestamp,
            'registration_number': 'abc-123',
        }],
        'areas': [{
            'start_time': '1970-01-01T00:00:00+00:00',
            'end_time': input_timestamp,
            'area': area_identifier,
        }],
    }

    if kind == 'single':
        response = enforcer_api_client.post(list_url, data=permit_data)
        data = response.data
    else:
        response = enforcer_api_client.post(list_url, data=[permit_data])
        data = response.data[0]

    assert response.status_code == HTTP_201_CREATED
    assert data['subjects'][0]['end_time'] == normalized_timestamp
    assert data['areas'][0]['end_time'] == normalized_timestamp


@pytest.mark.django_db
def test_lookup_item_is_created_for_permit(enforcer_api_client):
    permit_data = {
        'series': create_permit_series(owner=enforcer_api_client.auth_user).id,
        'external_id': generate_external_ids(),
        'subjects': generate_subjects(),
        'areas': generate_areas_data(enforcer_api_client),
    }
    assert PermitLookupItem.objects.count() == 0
    response = enforcer_api_client.post(list_url, data=permit_data)

    assert response.status_code == HTTP_201_CREATED
    assert PermitLookupItem.objects.count() == 1


def test_api_endpoint_returns_correct_data(enforcer_api_client, enforcer):
    create_permits(owner=enforcer.user, count=1)[0]

    response = enforcer_api_client.get(list_url)

    assert response.status_code == HTTP_200_OK
    check_permit_object_keys(response.data['results'][0])
    check_permit_subject_keys(response.data['results'][0]['subjects'][0])
    check_permit_areas_keys(response.data['results'][0]['areas'][0])


def check_permit_object_keys(data):
    assert set(data.keys()) == {'id', 'series', 'subjects', 'areas', 'external_id', 'properties'}


def check_permit_subject_keys(data):
    assert set(data.keys()) == {'start_time', 'end_time', 'registration_number'}


def check_permit_areas_keys(data):
    assert set(data.keys()) == {'start_time', 'end_time', 'area'}


def test_permit_data_matches_permit_object(enforcer_api_client, enforcer):
    permit = create_permits(owner=enforcer.user, count=1)[0]
    permit_detail_url = '{}{}/'.format(list_url, permit.id)

    response = enforcer_api_client.get(permit_detail_url)

    assert response.status_code == HTTP_200_OK
    assert response.data['id'] == permit.id
    assert response.data['series'] == permit.series.id
    assert response.data['subjects'] == permit.subjects
    assert response.data['areas'] == permit.areas
    check_permit_object_keys(response.data)
    check_permit_subject_keys(response.data['subjects'][0])
    check_permit_areas_keys(response.data['areas'][0])


def test_permit_bulk_create_creates_lookup_items(enforcer_api_client):
    permit_series = create_permit_series(owner=enforcer_api_client.auth_user)
    domain = enforcer_api_client.enforcer.enforced_domain
    user = enforcer_api_client.auth_user
    permit_data = [
        {
            "series": permit_series.id,
            "external_id": "E1",
            "subjects": generate_subjects(),
            "areas": generate_areas(domain=domain, allowed_user=user),
        },
        {
            "series": permit_series.id,
            "external_id": "E2",
            "subjects": generate_subjects(),
            "areas": generate_areas(domain=domain, allowed_user=user),
        },
    ]

    assert PermitLookupItem.objects.count() == 0
    response = enforcer_api_client.post(list_url, data=permit_data)

    assert response.status_code == HTTP_201_CREATED
    assert PermitLookupItem.objects.count() == 2


def test_permit_bulk_create_normalizes_timestamps(enforcer_api_client):
    user = enforcer_api_client.auth_user
    domain = enforcer_api_client.enforcer.enforced_domain
    permit = create_permits(owner=user, domain=domain, count=1)[0]
    area_code1 = permit.areas[0]['area']
    area_code2 = permit.areas[1]['area']
    permit_data = [
        {
            "series": permit.series.id,
            "external_id": "E1",
            'subjects': [{
                'start_time': '1970-01-01T01:23:00+01:23',
                'end_time': '2030-06-30T12:00+03:00',
                'registration_number': 'REG-1',
            }],
            'areas': [{
                'start_time': '1970-01-01T00:00:00Z',
                'end_time': '2030-06-30T11:00+02:00',
                'area': area_code1,
            }],
        },
        {
            "series": permit.series.id,
            "external_id": "E2",
            'subjects': [{
                'start_time': '1969-12-31T22:00:00-02:00',
                'end_time': '2030-06-30T10:00+01:00',
                'registration_number': 'REG-2',
            }],
            'areas': [{
                'start_time': '1970-01-01T00:00:00+00:00',
                'end_time': '2030-06-30T09:00Z',
                'area': area_code2,
            }],
        },
    ]

    response = enforcer_api_client.post(list_url, data=permit_data)

    assert response.status_code == HTTP_201_CREATED
    created_permits = Permit.objects.filter(external_id__in=['E1', 'E2'])
    (permit1, permit2) = list(created_permits.order_by('external_id'))
    assert permit1.subjects[0]['start_time'] == '1970-01-01T00:00:00+00:00'
    assert permit1.subjects[0]['end_time'] == '2030-06-30T09:00:00+00:00'
    assert permit1.areas[0]['start_time'] == '1970-01-01T00:00:00+00:00'
    assert permit1.areas[0]['end_time'] == '2030-06-30T09:00:00+00:00'
    assert permit2.subjects[0]['start_time'] == '1970-01-01T00:00:00+00:00'
    assert permit2.subjects[0]['end_time'] == '2030-06-30T09:00:00+00:00'
    assert permit2.areas[0]['start_time'] == '1970-01-01T00:00:00+00:00'
    assert permit2.areas[0]['end_time'] == '2030-06-30T09:00:00+00:00'


def test_permitseries_created_by_user_gets_the_user_as_owner(enforcer_api_client, enforcer):
    url = reverse('enforcement:v1:permitseries-list')

    response = enforcer_api_client.post(url, data={})

    assert response.status_code == HTTP_201_CREATED
    assert PermitSeries.objects.count() == 1
    assert PermitSeries.objects.first().owner == enforcer.user


def test_permit_visibility_is_limited_to_owner(
    enforcer_api_client, enforcer, operator,
):
    enforcer_owned_permit = create_permits(owner=enforcer.user, count=1)[0]
    create_permits(owner=operator.user, count=1)

    response = enforcer_api_client.get(list_url)

    assert response.status_code == HTTP_200_OK
    assert response.json()['count'] == 1
    assert response.json()['results'][0]['id'] == enforcer_owned_permit.id


def test_permit_series_visibility_is_limited_to_owner(
    enforcer_api_client, enforcer, operator
):
    url = reverse('enforcement:v1:permitseries-list')
    enforcer_owned_permitseries = create_permit_series(owner=enforcer.user)
    create_permit_series(owner=operator.user)

    response = enforcer_api_client.get(url)

    assert response.status_code == HTTP_200_OK
    assert response.json()['count'] == 1
    assert PermitSeries.objects.count() == 2
    assert response.json()['results'][0]['id'] == enforcer_owned_permitseries.id
