from django.contrib.gis.db.models.fields import MultiPolygonField
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('parkings', '0028_digital_disc_changes'),
    ]

    operations = [
        migrations.CreateModel(
            name='EnforcementDomain',
            fields=[
                ('id', models.AutoField(
                    auto_created=True,
                    primary_key=True,
                    serialize=False,
                    verbose_name='ID')),
                ('created_at', models.DateTimeField(
                    auto_now_add=True,
                    verbose_name='time created')),
                ('modified_at', models.DateTimeField(
                    auto_now=True,
                    verbose_name='time modified')),
                ('code', models.CharField(
                    max_length=10,
                    unique=True,
                    verbose_name='code')),
                ('name', models.CharField(max_length=40, verbose_name='name')),
                ('geom', MultiPolygonField(
                    srid=3879, verbose_name='geometry')),
            ],
            options={
                'ordering': ('code', ),
            },
        ),
        migrations.AddField(
            model_name='parking',
            name='domain',
            field=models.ForeignKey(
                to='parkings.EnforcementDomain',
                default=1,
                on_delete=models.PROTECT,
                related_name='parkings'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='permitarea',
            name='domain',
            field=models.ForeignKey(
                to='parkings.EnforcementDomain',
                default=1,
                on_delete=models.PROTECT,
                related_name='permit_areas'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='permitseries',
            name='owner',
            field=models.ForeignKey(
                to='parkings.Operator',
                blank=True,
                null=True,
                on_delete=models.PROTECT,
                related_name='permit_series_set'),
        ),
        migrations.AlterField(
            model_name='permitarea',
            name='identifier',
            field=models.CharField(max_length=10, verbose_name='identifier'),
        ),
        migrations.AlterUniqueTogether(
            name='permitarea',
            unique_together={('domain', 'identifier')},
        ),
    ]
