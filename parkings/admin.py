from django.contrib import admin
from django.contrib.gis.admin import OSMGeoAdmin

from .admin_utils import ReadOnlyAdmin, WithAreaField
from .models import (
    EnforcementDomain, Enforcer, Operator, Parking, ParkingArea, ParkingCheck,
    ParkingTerminal, PaymentZone, Permit, PermitArea, PermitLookupItem,
    PermitSeries, Region)


@admin.register(Enforcer)
class EnforcerAdmin(WithAreaField, OSMGeoAdmin):
    list_display = ['id', 'name', 'user', 'enforced_domain']
    ordering = ('name',)


@admin.register(EnforcementDomain)
class EnforcementDomainAdmin(WithAreaField, OSMGeoAdmin):
    list_display = ['id', 'code', 'name', 'area']
    ordering = ('code',)


@admin.register(Operator)
class OperatorAdmin(admin.ModelAdmin):
    list_display = ['name', 'user']


@admin.register(PaymentZone)
class PaymentZoneAdmin(WithAreaField, OSMGeoAdmin):
    list_display = ['id', 'number', 'name', 'area']
    ordering = ('number',)


@admin.register(Parking)
class ParkingAdmin(OSMGeoAdmin):
    date_hierarchy = 'time_start'
    list_display = [
        'id', 'operator', 'zone', 'parking_area', 'terminal_number',
        'time_start', 'time_end', 'registration_number',
        'created_at', 'modified_at']
    list_filter = ['operator', 'zone']
    ordering = ('-time_start',)


@admin.register(Region)
class RegionAdmin(WithAreaField, OSMGeoAdmin):
    list_display = ['id', 'name', 'capacity_estimate', 'area']
    ordering = ('name',)


@admin.register(ParkingArea)
class ParkingAreaAdmin(WithAreaField, OSMGeoAdmin):
    area_scale = 1
    list_display = ['id', 'origin_id', 'capacity_estimate', 'area']
    ordering = ('origin_id',)


@admin.register(ParkingCheck)
class ParkingCheckAdmin(ReadOnlyAdmin, OSMGeoAdmin):
    list_display = [
        'id', 'time', 'registration_number', 'location',
        'allowed', 'result', 'performer', 'created_at']

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
    date_hierarchy = 'created_at'
    list_display = ['id', 'series', 'external_id', 'created_at', 'modified_at']
    list_filter = ['series__active']
    ordering = ('-series', '-id')


@admin.register(PermitArea)
class PermitAreaAdmin(WithAreaField, OSMGeoAdmin):
    list_display = ['id', 'identifier', 'name', 'area']
    ordering = ('identifier',)


@admin.register(PermitLookupItem)
class PermitLookupItemAdmin(ReadOnlyAdmin):
    list_display = [
        'id', 'series', 'permit',
        'registration_number', 'area',
        'start_time', 'end_time']
    list_filter = ['permit__series__active']
    ordering = ('-permit__series', 'permit')

    def series(self, instance):
        series = instance.permit.series
        return '{id}{active}'.format(
            id=series.id, active='*' if series.active else '')


@admin.register(PermitSeries)
class PermitSeriesAdmin(admin.ModelAdmin):
    date_hierarchy = 'created_at'
    list_display = ['id', 'active', 'created_at', 'modified_at']
    list_filter = ['active']
    ordering = ('-created_at', '-id')
