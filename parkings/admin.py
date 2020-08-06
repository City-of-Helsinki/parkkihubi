from django.contrib import admin
from django.contrib.gis.admin import OSMGeoAdmin
from django.db import models

from .admin_utils import ReadOnlyAdmin, WithAreaField
from .models import (
    ArchivedParking, EnforcementDomain, Enforcer, Monitor, Operator, Parking,
    ParkingArea, ParkingCheck, ParkingTerminal, PaymentZone, Permit,
    PermitArea, PermitLookupItem, PermitSeries, Region)


@admin.register(Enforcer)
class EnforcerAdmin(WithAreaField, OSMGeoAdmin):
    list_display = ['id', 'name', 'user', 'enforced_domain']
    ordering = ('name',)


@admin.register(EnforcementDomain)
class EnforcementDomainAdmin(WithAreaField, OSMGeoAdmin):
    list_display = ['id', 'code', 'name', 'area']
    ordering = ('code',)


@admin.register(Monitor)
class MonitorAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'domain']
    list_filter = ['domain']


@admin.register(Operator)
class OperatorAdmin(admin.ModelAdmin):
    list_display = ['name', 'user']


@admin.register(PaymentZone)
class PaymentZoneAdmin(WithAreaField, OSMGeoAdmin):
    list_display = ['id', 'domain', 'number', 'name', 'area']
    list_filter = ['domain']
    ordering = ('number',)


@admin.register(Parking, ArchivedParking)
class ParkingAdmin(OSMGeoAdmin):
    date_hierarchy = 'time_start'
    list_display = [
        'id', 'operator', 'domain', 'zone', 'parking_area', 'terminal_number',
        'time_start', 'time_end', 'registration_number',
        'created_at', 'modified_at']
    list_filter = ['operator', 'domain', 'zone']
    ordering = ('-time_start',)
    search_fields = ['registration_number']


@admin.register(Region)
class RegionAdmin(WithAreaField, OSMGeoAdmin):
    list_display = ['id', 'domain', 'name', 'capacity_estimate', 'area']
    list_filter = ['domain']
    ordering = ('name',)


@admin.register(ParkingArea)
class ParkingAreaAdmin(WithAreaField, OSMGeoAdmin):
    area_scale = 1
    list_display = ['id', 'origin_id', 'domain', 'capacity_estimate', 'area']
    list_filter = ['domain']
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
    list_display = ['id', 'domain', 'number', 'name']
    list_filter = ['domain']


@admin.register(Permit)
class PermitAdmin(admin.ModelAdmin):
    date_hierarchy = 'created_at'
    list_display = [
        'id', 'domain', 'series', 'external_id',
        'item_count', 'created_at', 'modified_at']
    list_filter = ['series__active', 'domain', 'series__owner']
    ordering = ('-series', '-id')

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.annotate(item_count=models.Count('lookup_items'))

    def item_count(self, instance):
        return instance.item_count


@admin.register(PermitArea)
class PermitAreaAdmin(WithAreaField, OSMGeoAdmin):
    list_display = ['id', 'domain', 'identifier', 'name', 'area']
    list_filter = ['domain']
    ordering = ('identifier',)


@admin.register(PermitLookupItem)
class PermitLookupItemAdmin(ReadOnlyAdmin):
    date_hierarchy = 'start_time'
    list_display = [
        'id', 'series', 'domain', 'permit',
        'registration_number', 'area',
        'start_time', 'end_time']
    list_filter = [
        'permit__series__active',
        'permit__domain',
        'permit__series__owner']
    ordering = ('-permit__series', 'permit')
    search_fields = ['registration_number']

    def series(self, instance):
        series = instance.permit.series
        return '{id}{active}'.format(
            id=series.id, active='*' if series.active else '')

    def domain(self, instance):
        return instance.permit.domain


@admin.register(PermitSeries)
class PermitSeriesAdmin(admin.ModelAdmin):
    date_hierarchy = 'created_at'
    list_display = [
        'id', 'active', 'owner', 'permit_count',
        'created_at', 'modified_at']
    list_filter = ['active', 'owner']
    ordering = ('-created_at', '-id')

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.annotate(permit_count=models.Count('permit'))

    def permit_count(self, instance):
        return instance.permit_count
