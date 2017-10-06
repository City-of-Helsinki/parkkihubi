from __future__ import unicode_literals

from django.db import migrations
from django.db.models import Q

from ..models import Parking


def fill_normalized_reg_nums(apps, schema_editor):
    parking_model = apps.get_model('parkings', 'Parking')
    parkings_to_process = parking_model.objects.filter(
        Q(normalized_reg_num=None) | Q(normalized_reg_num=''))
    for parking in parkings_to_process:
        parking.normalized_reg_num = Parking.normalize_reg_num(
            parking.registration_number)
        parking.save(update_fields=['normalized_reg_num'])


class Migration(migrations.Migration):
    dependencies = [
        ('parkings', '0014_normalized_reg_num'),
    ]

    operations = [
        migrations.RunPython(
            code=fill_normalized_reg_nums,
            reverse_code=migrations.RunPython.noop),
    ]
