# Generated by Django 2.2.10 on 2020-04-28 06:08
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


def _set_domain(apps, schema_editor):
    region_mode = apps.get_model('parkings', 'Region')
    regions = region_mode.objects.filter(domain__isnull=True)
    if regions.exists():
        regions.update(domain=_get_or_create_domain(apps))


def _get_or_create_domain(apps):
    name, code = getattr(settings, "DEFAULT_ENFORCEMENT_DOMAIN")
    enforcement_domain_model = apps.get_model('parkings', 'EnforcementDomain')
    domain, created = enforcement_domain_model.objects.get_or_create(name=name, code=code)
    return domain


class Migration(migrations.Migration):

    dependencies = [
        ("parkings", "0036_monitor"),
    ]

    operations = [
        migrations.AddField(
            model_name="region",
            name="domain",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="regions",
                to="parkings.EnforcementDomain",
            ),
        ),
        migrations.RunPython(_set_domain, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="region",
            name="domain",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name="regions",
                to="parkings.EnforcementDomain",
            ),
        ),
    ]
