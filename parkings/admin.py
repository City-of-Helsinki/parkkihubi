from django.contrib import admin
from django.contrib.gis.admin import OSMGeoAdmin

from .admin_utils import ReadOnlyAdmin
from .models import (
    Operator, Parking, ParkingArea, ParkingCheck, ParkingTerminal, PaymentZone,
    Permit, PermitArea, PermitLookupItem, Region)


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


@admin.register(ParkingCheck)
class ParkingCheckAdmin(ReadOnlyAdmin, OSMGeoAdmin):
    modifiable = False

    def get_readonly_fields(self, request, obj=None):
        # Remove location from readonly fields, because otherwise the
        # map won't be rendered at all.  The class level
        # "modifiable=False" will take care of not allowing the location
        # to be modified.
        fields = super().get_readonly_fields(request, obj)
        return [x for x in fields if x != 'location']

    def has_change_permission(self, request, obj=None):
        # Needed to make the map visible for the location field
        return True


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
