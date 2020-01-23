from django.contrib import admin


class ReadOnlyAdmin(admin.ModelAdmin):
    def get_readonly_fields(self, request, obj=None):
        return [x.name for x in obj._meta.fields]

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


class WithAreaField:
    area_scale = 1000000

    def area(self, instance):
        if not instance.geom:
            return ''
        assert self.area_scale in [1000000, 1]
        unit = 'km\u00b2' if self.area_scale == 1000000 else 'm\u00b2'
        return '{area:.1f} {unit}'.format(
            area=instance.geom.area / self.area_scale, unit=unit)
