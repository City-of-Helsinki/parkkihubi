# Generated by Django 2.2.10 on 2020-04-27 10:52

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('parkings', '0035_parkings_payment_zone_fk_change'),
    ]

    operations = [
        migrations.CreateModel(
            name='Monitor',
            fields=[
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='time created')),
                ('modified_at', models.DateTimeField(auto_now=True, verbose_name='time modified')),
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=80, verbose_name='name')),
                ('domain', models.ForeignKey(help_text='The enforcement domain user can monitor', on_delete=django.db.models.deletion.PROTECT, to='parkings.EnforcementDomain')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL, verbose_name='user')),
            ],
            options={
                'verbose_name': 'monitor',
                'verbose_name_plural': 'monitors',
            },
        ),
    ]