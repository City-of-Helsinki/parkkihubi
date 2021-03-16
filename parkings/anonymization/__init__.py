from django.conf import settings
from django.db import transaction
from django.utils import timezone

from ..models import Parking, ParkingCheck, PermitLookupItem


def anonymize_parking_registration_numbers():
    parkings = (
        Parking.objects.filter(time_end__lt=get_past_time())
        .exclude(registration_number="")
        .order_by("time_end")
    )

    for parking in parkings:
        with transaction.atomic():
            parking.registration_number = ""
            parking.normalized_reg_num = ""
            parking.save(update_fields=["registration_number", "normalized_reg_num"])


def anonymize_parking_check_registration_numbers():
    parking_checks = (
        ParkingCheck.objects.filter(created_at__lt=get_past_time())
        .exclude(registration_number="")
        .order_by("created_at")
    )

    for parking_check in parking_checks:
        with transaction.atomic():
            parking_check.registration_number = ""
            parking_check.save(update_fields=["registration_number"])


def anonymize_permit_registration_numbers():
    parking_lookups = (
        PermitLookupItem.objects.filter(end_time__lt=get_past_time())
        .exclude(registration_number="")
        .order_by("end_time")
    )

    for permits_lookup in parking_lookups:
        with transaction.atomic():
            permit = permits_lookup.permit
            subjects = permit.subjects
            for sub in subjects:
                sub["registration_number"] = ""
            permit.save(update_fields=["subjects"])


def get_past_time():
    time = timezone.now()
    grace_duration = getattr(settings, "PARKKIHUBI_ANONYMIZE_REG_NUM_BEFORE", None)
    past_time = time - grace_duration
    return past_time
