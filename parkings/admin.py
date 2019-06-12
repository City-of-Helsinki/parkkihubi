from django.contrib import admin
from django.contrib.gis.admin import OSMGeoAdmin

from parkings.models import PaymentZone, PermitArea

from .models import (
    Operator, Parking, ParkingArea, ParkingTerminal, Permit, PermitCacheItem,
    Region)


class OperatorAdmin(admin.ModelAdmin):
    pass


class PermitAreaAdmin(admin.ModelAdmin):
    ordering = ('identifier',)


class PaymentZoneAdmin(admin.ModelAdmin):
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


class ParkingAreaAdmin(OSMGeoAdmin):
    ordering = ('origin_id',)


@admin.register(ParkingTerminal)
class ParkingTerminalAdmin(OSMGeoAdmin):
    list_display = ['id', 'number', 'name']


admin.site.register(Operator, OperatorAdmin)
admin.site.register(ParkingArea, ParkingAreaAdmin)
admin.site.register(Permit)
admin.site.register(PermitCacheItem)
admin.site.register(PermitArea, PermitAreaAdmin)
admin.site.register(PaymentZone, PaymentZoneAdmin)
