from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('parkings', '0015_fill_normalized_reg_nums'),
    ]

    operations = [
        migrations.AlterField(
            model_name='parking',
            name='normalized_reg_num',
            field=models.CharField(
                db_index=True, max_length=20,
                verbose_name='normalized registration number'),
        ),
    ]
