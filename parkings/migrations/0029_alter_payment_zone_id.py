
from django.db import migrations, models


def _generate_payment_zone_ids(apps, schema_editor):
    payment_zone_model = apps.get_model('parkings', 'PaymentZone')
    for payment_zone in payment_zone_model.objects.all():
        payment_zone.tmp_id = payment_zone.number
        payment_zone.save(update_fields=['tmp_id'])


class Migration(migrations.Migration):

    dependencies = [
        ('parkings', '0028_digital_disc_changes'),
    ]

    operations = [
        migrations.AddField(
            model_name='paymentzone',
            name='tmp_id',
            field=models.IntegerField(null=True),
        ),
        migrations.RunPython(_generate_payment_zone_ids, migrations.RunPython.noop),
        migrations.RemoveField('paymentzone', 'id'),
        migrations.AlterField(
            model_name='paymentzone',
            name='tmp_id',
            field=models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
        migrations.RenameField(
            model_name='paymentzone',
            old_name='tmp_id',
            new_name='id'
        ),
    ]
