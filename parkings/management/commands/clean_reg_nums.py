#!/usr/bin/env python
"""
Anonymize the registration number from ArchivedParking, Parking, ParkingCheck and Permit
that are expired 24 hours ago.
"""
from django.core.management.base import BaseCommand

from parkings.anonymization import (
    anonymize_archived_parking_registration_numbers,
    anonymize_parking_check_registration_numbers,
    anonymize_parking_registration_numbers,
    anonymize_permit_registration_numbers)


class Command(BaseCommand):
    help = __doc__.strip().splitlines()[0]

    def handle(self, *args, **options):
        anonymize_archived_parking_registration_numbers()
        anonymize_parking_registration_numbers()
        anonymize_parking_check_registration_numbers()
        anonymize_permit_registration_numbers()
