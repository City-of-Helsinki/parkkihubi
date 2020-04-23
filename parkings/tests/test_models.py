import datetime

import pytest
from django.contrib.gis.geos import Point
from django.test import override_settings
from django.utils.timezone import now, utc

from parkings.factories.parking import create_payment_zone
from parkings.models import Operator, Parking, ParkingCheck, ParkingTerminal


def test_operator_instance_creation():
    Operator(name="name", user_id=1)


@pytest.mark.django_db
def test_parking_instance_creation(enforcer):
    create_parking(enforcer)


def create_parking(enforcer, operator_id=1, registration_number='ABC-123', **kwargs):
    return Parking(
        location=Point(60.193609, 24.951394),
        operator_id=operator_id,
        registration_number=registration_number,
        time_end=now() + datetime.timedelta(days=1),
        time_start=now(),
        zone=create_payment_zone(domain=enforcer.enforced_domain),
        **kwargs
    )


@pytest.mark.django_db
@override_settings(TIME_ZONE='Europe/Helsinki')
def test_parking_str(parking_factory):
    parking = parking_factory(
        time_start=datetime.datetime(2014, 1, 1, 6, 0, 0, tzinfo=utc),
        time_end=datetime.datetime(2016, 1, 1, 7, 0, 0, tzinfo=utc),
        registration_number='ABC-123',
    )
    assert all(str(parking).count(val) == 1 for val in ('2014', '2016', '8', '9', 'ABC-123'))

    parking = parking_factory(
        time_start=datetime.datetime(2016, 1, 1, 6, 0, 0, tzinfo=utc),
        time_end=datetime.datetime(2016, 1, 1, 7, 0, 0, tzinfo=utc),
        registration_number='ABC-123',
    )
    assert all(str(parking).count(val) == 1 for val in ('2016', '8', '9', 'ABC-123'))

    parking = parking_factory(
        time_start=datetime.datetime(2016, 1, 1, 6, 0, 0, tzinfo=utc),
        time_end=None,
        registration_number='ABC-123',
    )
    assert all(str(parking).count(val) == 1 for val in ('2016', '8', 'ABC-123'))


def test_parking_check_str():
    parking_check = ParkingCheck(
        created_at=datetime.datetime(2014, 1, 1, 6, 0, 0, tzinfo=utc),
        time=datetime.datetime(2015, 1, 1, 12, 0, 0, tzinfo=utc),
        time_overridden=True,
        registration_number='ABC-123',
        location=Point(60.193609, 24.951394),
        result={'location': {'payment_zone': 2, 'permit_area': 'J'}},
        allowed=True,
        found_parking=None,
    )

    result = str(parking_check)

    assert result == (
        '[2014-01-01 06:00:00+00:00]'
        ' 2015-01-01 12:00:00+00:00* 24.95139N 60.19361E Z2/J ABC-123: OK')


@pytest.mark.django_db
def test_terminal_set_on_save(admin_user, enforcer):
    operator = Operator.objects.get_or_create(user=admin_user)[0]
    terminal = ParkingTerminal.objects.get_or_create(number=1234)[0]
    parking = create_parking(enforcer, operator_id=operator.pk, terminal_number=1234)
    assert parking.terminal_number == 1234
    assert parking.terminal is None
    parking.save()
    assert parking.terminal == terminal


@pytest.mark.django_db
def test_location_set_from_terminal(admin_user, enforcer):
    operator = Operator.objects.get_or_create(user=admin_user)[0]
    terminal = ParkingTerminal.objects.get_or_create(
        number=4567, defaults={
            'location': Point(61, 25), 'name': "Test terminal"})[0]
    parking = create_parking(enforcer, operator_id=operator.pk, terminal_number=4567)
    parking.location = None
    parking.save()
    assert parking.location == terminal.location


@pytest.mark.django_db
def test_parking_save_with_nondigit_terminal_number(admin_user, enforcer):
    operator = Operator.objects.get_or_create(user=admin_user)[0]
    parking = create_parking(enforcer, operator_id=operator.pk, terminal_number='123a')
    parking.location = None
    parking.save()
    assert parking.terminal is None
    assert parking.location is None
    assert parking.terminal_number == '123a'


@pytest.mark.django_db
def test_location_not_overridden_from_terminal(admin_user, enforcer):
    operator = Operator.objects.get_or_create(user=admin_user)[0]
    terminal = ParkingTerminal.objects.get_or_create(
        number=4567, defaults={
            'location': Point(61, 25), 'name': "Test terminal"})[0]
    parking = create_parking(enforcer, operator_id=operator.pk, terminal_number=4567)
    location = parking.location
    parking.save()
    assert parking.location == location
    assert parking.location != terminal.location


def test_parking_terminal_str():
    terminal = ParkingTerminal(
        number=4567, location=Point(61, 25), name="Test terminal")
    assert '{}'.format(terminal) == "4567: Test terminal"


@pytest.mark.django_db
@pytest.mark.parametrize('reg_num,normalized', [
    ('ABC-123', 'ABC123'),
    ('ABC123', 'ABC123'),
    ('abc-123', 'ABC123'),
    ('Xyz-456', 'XYZ456'),
    ('Xyz-456-123', 'XYZ456123'),
    ('Cool Reg 42', 'COOLREG42'),
])
def test_normalized_reg_num(admin_user, reg_num, normalized, enforcer):
    operator = Operator.objects.get_or_create(user=admin_user)[0]
    parking = create_parking(
        enforcer,
        operator_id=operator.pk,
        registration_number=reg_num)
    assert parking.registration_number == reg_num
    assert not parking.normalized_reg_num
    parking.save()
    assert parking.registration_number == reg_num
    assert parking.normalized_reg_num == normalized


@pytest.mark.parametrize('reg_num,result', [
    (None, ''),
    ('', ''),
    ('A', 'A'),
    ('a', 'A'),
    ('ABC-123', 'ABC123'),
    ('abc/123', 'ABC/123'),
    ('X Y Z - 3  2 9 4', 'XYZ3294'),
    ('3.4.5-6.7', '3.4.56.7'),
    (' ', ''),
    ('-', ''),
    ('123--ABC', '123ABC'),
])
def test_normalize_reg_num_function(reg_num, result):
    assert Parking.normalize_reg_num(reg_num) == result


@pytest.mark.django_db
@pytest.mark.parametrize('code,result', [('1', 1), ('1A', '1A'), ])
def test_zone_casted_code(code, result):
    zone = create_payment_zone(code=code)
    assert zone.casted_code == result
