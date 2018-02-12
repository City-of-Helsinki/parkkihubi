from django.contrib import admin
from django.contrib.gis.admin import OSMGeoAdmin

from .models import Operator, Parking, ParkingArea, ParkingTerminal, Region


class OperatorAdmin(admin.ModelAdmin):
    pass


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
