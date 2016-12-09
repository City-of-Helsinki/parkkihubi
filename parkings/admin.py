from django.contrib import admin

from .models import Operator, Parking


class OperatorAdmin(admin.ModelAdmin):
    pass


class ParkingAdmin(admin.ModelAdmin):
    pass


admin.site.register(Operator, OperatorAdmin)
admin.site.register(Parking, ParkingAdmin)
