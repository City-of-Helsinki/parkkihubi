from django.conf import settings
from django.utils import timezone

from ..models import ArchivedParking, Parking, ParkingCheck, PermitLookupItem


def anonymize_archived_parking_registration_numbers():
    ArchivedParking.objects.unanonymized().ends_before(anonymization_instant()).anonymize()


def anonymize_parking_registration_numbers():
    Parking.objects.unanonymized().ends_before(anonymization_instant()).anonymize()


def anonymize_parking_check_registration_numbers():
    ParkingCheck.objects.unanonymized().created_before(anonymization_instant()).anonymize()


def anonymize_permit_registration_numbers():
    PermitLookupItem.objects.unanonymized().ends_before(anonymization_instant()).anonymize()


def anonymization_instant():
    grace_duration = getattr(settings, "PARKKIHUBI_REGISTRATION_NUMBERS_REMOVABLE_AFTER")
    return timezone.now() - grace_duration
