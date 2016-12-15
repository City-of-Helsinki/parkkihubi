from django.contrib import admin

from .models import Address, Operator, Parking


class AddressAdmin(admin.ModelAdmin):
    pass


class OperatorAdmin(admin.ModelAdmin):
    pass


class ParkingAdmin(admin.ModelAdmin):
    pass


admin.site.register(Address, AddressAdmin)
admin.site.register(Operator, OperatorAdmin)
admin.site.register(Parking, ParkingAdmin)
