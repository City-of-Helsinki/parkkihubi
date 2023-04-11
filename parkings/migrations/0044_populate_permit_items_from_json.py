import logging

from django.db import migrations

from ..models import Parking

LOG = logging.getLogger(__name__)


def populate_permit_subject_and_area_items(apps, schema_editor):
    """
    Populate PermitSubjectItem and PermitAreaItem tables from Permit.

    Use the JSON fields permit.subjects and permit.areas to populate the
    PermitSubjectItem and PermitAreaItem tables.

    Also link the created PermitSubjectItem and PermitAreaItem objects
    to existing PermitLookupItem objects.
    """
    permit_model = apps.get_model("parkings", "Permit")
    subject_item_model = apps.get_model("parkings", "PermitSubjectItem")
    area_item_model = apps.get_model("parkings", "PermitAreaItem")
    lookup_item_model = apps.get_model("parkings", "PermitLookupItem")
    area_model = apps.get_model("parkings", "PermitArea")

    # Generate a cache of all PermitArea objects to avoid unnecessary
    # database queries.
    #
    # area_cache is a mapping from domain id to a mapping from area
    # identifier to area id
    area_cache = {}
    for area in area_model.objects.all():
        area_cache.setdefault(area.domain_id, {})[area.identifier] = area.id

    LOG.info("Processing permits with no subjects...")
    permits = permit_model.objects.filter(subjects=[])
    count = permits.count()
    for (i, permit) in enumerate(permits):
        if i % 10000 == 0:
            LOG.info("Processed %9d/%d permits", i, count)
        area_map = area_cache[permit.domain_id]
        create_area_items(permit, area_item_model, area_map)

    LOG.info("Processing permits with subjects...")
    permits = permit_model.objects.exclude(subjects=[])
    count = permits.count()
    for (i, permit) in enumerate(permits):
        if i % 1000 == 0:
            LOG.info("Processed %9d/%d permits", i, count)
        area_map = area_cache[permit.domain_id]
        subject_items = create_subject_items(permit, subject_item_model)
        area_items = create_area_items(permit, area_item_model, area_map)
        update_lookup_items(permit, subject_items, area_items,
                            lookup_item_model)


def create_area_items(permit, area_item_model, area_map):
    area_items = [
        area_item_model(
            permit=permit,
            start_time=area["start_time"],
            end_time=area["end_time"],
            area_id=area_map[area["area"]],
        )
        for area in permit.areas
    ]
    area_item_model.objects.bulk_create(area_items)
    return area_items


def create_subject_items(permit, subject_item_model):
    subject_items = [
        subject_item_model(
            permit=permit,
            start_time=subject["start_time"],
            end_time=subject["end_time"],
            registration_number=subject["registration_number"],
        )
        for subject in permit.subjects
    ]
    subject_item_model.objects.bulk_create(subject_items)
    return subject_items


def update_lookup_items(permit, subject_items, area_items, lookup_item_model):
    for subject_item in subject_items:
        for area_item in area_items:
            start_time = max(subject_item.start_time, area_item.start_time)
            end_time = min(subject_item.end_time, area_item.end_time)
            if start_time <= end_time:
                normalized_reg_num = Parking.normalize_reg_num(
                    subject_item.registration_number)
                lookup_items = lookup_item_model.objects.filter(
                    permit=permit,
                    registration_number=normalized_reg_num,
                    area=area_item.area,
                    start_time=start_time,
                    end_time=end_time,
                )
                lookup_items.update(
                    subject_item=subject_item,
                    area_item=area_item,
                )


class Migration(migrations.Migration):
    dependencies = [
        ("parkings", "0043_permit_subject_and_area_items"),
    ]

    operations = [
        migrations.RunPython(
            populate_permit_subject_and_area_items,
            migrations.RunPython.noop,
        ),
    ]
