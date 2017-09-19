from django.contrib import admin
from django.contrib.gis.admin import OSMGeoAdmin

from .models import Operator, Parking, ParkingArea, ParkingTerminal


class OperatorAdmin(admin.ModelAdmin):
    pass


class ParkingAreaAdmin(OSMGeoAdmin):
    ordering = ('origin_id',)


@admin.register(ParkingTerminal)
class ParkingTerminalAdmin(OSMGeoAdmin):
    list_display = ['id', 'number', 'name']


admin.site.register(Operator, OperatorAdmin)
admin.site.register(Parking, OSMGeoAdmin)
admin.site.register(ParkingArea, ParkingAreaAdmin)
