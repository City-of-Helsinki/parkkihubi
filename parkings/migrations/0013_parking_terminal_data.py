from __future__ import unicode_literals

from django.core.management import call_command
from django.db import migrations


def noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):
    dependencies = [
        ('parkings', '0012_parking_terminal'),
    ]

    operations = [
        migrations.RunPython(code=noop, reverse_code=noop),
    ]
