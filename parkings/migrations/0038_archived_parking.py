# Generated by Django 2.2.12 on 2020-06-09 14:06

import django.contrib.gis.db.models.fields
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('parkings', '0037_region_domain'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='parking',
            options={'default_related_name': 'parkings', 'verbose_name': 'parking', 'verbose_name_plural': 'parkings'},
        ),
        migrations.AlterField(
            model_name='parking',
            name='terminal',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='parkings', to='parkings.ParkingTerminal', verbose_name='terminal'),
        ),
        migrations.CreateModel(
            name='ArchivedParking',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('terminal_number', models.CharField(blank=True, max_length=50, verbose_name='terminal number')),
                ('location', django.contrib.gis.db.models.fields.PointField(blank=True, null=True, srid=4326, verbose_name='location')),
                ('registration_number', models.CharField(db_index=True, max_length=20, verbose_name='registration number')),
                ('normalized_reg_num', models.CharField(db_index=True, max_length=20, verbose_name='normalized registration number')),
                ('time_start', models.DateTimeField(db_index=True, verbose_name='parking start time')),
                ('time_end', models.DateTimeField(blank=True, db_index=True, null=True, verbose_name='parking end time')),
                ('is_disc_parking', models.BooleanField(default=False, verbose_name='disc parking')),
                ('created_at', models.DateTimeField(verbose_name='time created')),
                ('modified_at', models.DateTimeField(verbose_name='time modified')),
                ('archived_at', models.DateTimeField(auto_now_add=True, verbose_name='time archived')),
                ('domain', models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, related_name='archived_parkings', to='parkings.EnforcementDomain')),
                ('operator', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='archived_parkings', to='parkings.Operator', verbose_name='operator')),
                ('parking_area', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='archived_parkings', to='parkings.ParkingArea', verbose_name='parking area')),
                ('region', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='archived_parkings', to='parkings.Region', verbose_name='region')),
                ('terminal', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='archived_parkings', to='parkings.ParkingTerminal', verbose_name='terminal')),
                ('zone', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='archived_parkings', to='parkings.PaymentZone', verbose_name='PaymentZone')),
            ],
            options={
                'verbose_name': 'archived parking',
                'verbose_name_plural': 'archived parkings',
                'default_related_name': 'archived_parkings',
            },
        ),
    ]