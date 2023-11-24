# Migration to populate the PermitArea.allowed_users field

from django.db import migrations


def populate_allowed_users_from_permitted_user(apps, schema_editor):
    permit_area_model = apps.get_model("parkings", "PermitArea")
    for permit_area in permit_area_model.objects.all():
        permit_area.allowed_users.add(permit_area.permitted_user)


def populate_permitted_user_from_allowed_users(apps, schema_editor):
    permit_area_model = apps.get_model("parkings", "PermitArea")
    for permit_area in permit_area_model.objects.all():
        permit_area.permitted_user = permit_area.allowed_users.first()
        permit_area.save()


class Migration(migrations.Migration):
    dependencies = [
        ("parkings", "0046_permitarea_allowed_users"),
    ]

    operations = [
        migrations.RunPython(
            populate_allowed_users_from_permitted_user,
            populate_permitted_user_from_allowed_users,
        ),
    ]
