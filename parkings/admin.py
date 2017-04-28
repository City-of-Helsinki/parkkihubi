from django.contrib import admin
from django.contrib.gis.admin import OSMGeoAdmin

from .models import Operator, Parking, ParkingArea


class OperatorAdmin(admin.ModelAdmin):
    pass


admin.site.register(Operator, OperatorAdmin)
admin.site.register(Parking, OSMGeoAdmin)
admin.site.register(ParkingArea, OSMGeoAdmin)
