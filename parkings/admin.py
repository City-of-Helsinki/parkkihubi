from django.contrib import admin
from django.contrib.gis.admin import OSMGeoAdmin

from parkings.models import PaymentZone, PermitArea

from .admin_utils import ReadOnlyAdmin
from .models import (
    Operator, Parking, ParkingArea, ParkingTerminal, Permit, PermitLookupItem,
    Region)


@admin.register(Operator)
class OperatorAdmin(admin.ModelAdmin):
    pass


@admin.register(PaymentZone)
class PaymentZoneAdmin(OSMGeoAdmin):
    ordering = ('number',)


@admin.register(Parking)
class ParkingAdmin(OSMGeoAdmin):
    list_display = [
        'id', 'operator', 'zone', 'parking_area', 'terminal_number',
        'time_start', 'time_end', 'registration_number',
        'created_at', 'modified_at']
    list_filter = ['operator', 'zone']
    ordering = ('-created_at',)


@admin.register(Region)
class RegionAdmin(OSMGeoAdmin):
    ordering = ('name',)


@admin.register(ParkingArea)
class ParkingAreaAdmin(OSMGeoAdmin):
    ordering = ('origin_id',)


@admin.register(ParkingTerminal)
class ParkingTerminalAdmin(OSMGeoAdmin):
    list_display = ['id', 'number', 'name']


@admin.register(Permit)
class PermitAdmin(admin.ModelAdmin):
    pass


@admin.register(PermitArea)
class PermitAreaAdmin(OSMGeoAdmin):
    ordering = ('identifier',)


@admin.register(PermitLookupItem)
class PermitLookupItemAdmin(ReadOnlyAdmin):
    pass
