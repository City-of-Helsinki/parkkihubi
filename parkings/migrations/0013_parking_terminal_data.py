from __future__ import unicode_literals

from django.core.management import call_command
from django.db import migrations


def load_parking_terminals_from_fixture(apps, schema_editor):
    call_command('loaddata', 'parking_terminals',
                 verbosity=0)


def noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):
    dependencies = [
        ('parkings', '0012_parking_terminal'),
    ]

    operations = [
        migrations.RunPython(
            code=load_parking_terminals_from_fixture,
            reverse_code=noop),
    ]
