import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('parkings', '0017_region'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='parkingarea',
            name='region', ),
        migrations.AddField(
            model_name='parking',
            name='region',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='parkings',
                to='parkings.Region',
                verbose_name='region')),
        migrations.AddField(
            model_name='region',
            name='capacity_estimate',
            field=models.PositiveIntegerField(
                blank=True, null=True, verbose_name='capacity estimate')),
    ]
