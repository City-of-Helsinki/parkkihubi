from datetime import timedelta

from django.conf import settings
from django.contrib.gis.geos import MultiPolygon
from django.db import migrations
from django.db.models import Q
from django.utils import timezone


def _set_domains(apps, schema_editor):
    parking_model = apps.get_model('parkings', 'Parking')
    parking_area_model = apps.get_model('parkings', 'ParkingArea')
    payment_zone_model = apps.get_model('parkings', 'PaymentZone')
    parking_terminal_model = apps.get_model('parkings', 'ParkingTerminal')
    permit_model = apps.get_model('parkings', 'Permit')
    permit_area_model = apps.get_model('parkings', 'PermitArea')

    time = timezone.now() - timedelta(days=7)
    parkings = parking_model.objects.filter(domain=None).filter(
        Q(time_end__gte=time) | Q(time_end=None))
    if parkings.exists():
        parkings.update(domain=_get_or_create_enforcement_domain(apps))

    parking_areas = parking_area_model.objects.filter(domain=None)
    if parking_areas.exists():
        parking_areas.update(domain=_get_or_create_enforcement_domain(apps))

    parking_terminals = parking_terminal_model.objects.filter(domain=None)
    if parking_terminals.exists():
        parking_terminals.update(domain=_get_or_create_enforcement_domain(apps))

    permits = permit_model.objects.filter(domain=None)
    if permits.exists():
        permits.update(domain=_get_or_create_enforcement_domain(apps))

    permit_areas = permit_area_model.objects.filter(domain=None)
    if permit_areas.exists():
        permit_areas.update(domain=_get_or_create_enforcement_domain(apps),
                            permitted_user=_get_or_create_pasi_user(apps))

    payment_zones = payment_zone_model.objects.filter(domain=None)
    if payment_zones.exists():
        payment_zones.update(domain=_get_or_create_enforcement_domain(apps))

    for payment_zone in payment_zone_model.objects.filter(code=None):
        payment_zone.code = str(payment_zone.number)
        payment_zone.save(update_fields=["code"])


def _set_permitseries_owner(apps, schema_editor):
    permit_series_model = apps.get_model('parkings', 'PermitSeries')
    permit_series = permit_series_model.objects.filter(owner=None)
    if permit_series.exists():
        permit_series.update(owner=_get_or_create_pasi_user(apps))


def _create_enforcer_for_user(apps, schema_editor):
    user_model = apps.get_model(settings.AUTH_USER_MODEL)
    for user in user_model.objects.filter(is_staff=True):
        _get_or_create_enforcer(apps, user)


def _get_or_create_enforcer(apps, user):
    enforcer_model = apps.get_model('parkings', 'Enforcer')
    enforcer, created = enforcer_model.objects.get_or_create(
        name=user.username,
        defaults={
            'user': user,
            'enforced_domain': _get_or_create_enforcement_domain(apps),
        }
    )
    return enforcer


def _get_or_create_pasi_user(apps):
    user_model = apps.get_model(settings.AUTH_USER_MODEL)
    permit_owner, created = user_model.objects.get_or_create(
        username='PASI',
        defaults={
            'is_staff': True
        }
    )
    return permit_owner


def _get_or_create_enforcement_domain(apps):
    payment_zone_model = apps.get_model('parkings', 'PaymentZone')
    enforcement_domain_model = apps.get_model('parkings', 'EnforcementDomain')
    domain_geom = None
    for payment_zone in payment_zone_model.objects.all():
        if domain_geom is None:
            domain_geom = payment_zone.geom
        else:
            domain_geom |= payment_zone.geom

    if not isinstance(domain_geom, MultiPolygon):
        domain_geom = MultiPolygon(domain_geom)

    name, code = getattr(settings, "DEFAULT_ENFORCEMENT_DOMAIN")
    enforcement_domain, created = enforcement_domain_model.objects.get_or_create(
        code=code,
        defaults={
            "name": name,
            "geom": domain_geom,
        }
    )
    return enforcement_domain


class Migration(migrations.Migration):
    dependencies = [
        ('parkings', '0031_enforcement_domain'),
    ]

    operations = [
        migrations.RunPython(_set_domains, migrations.RunPython.noop),
        migrations.RunPython(_create_enforcer_for_user, migrations.RunPython.noop),
        migrations.RunPython(_set_permitseries_owner, migrations.RunPython.noop),
    ]
