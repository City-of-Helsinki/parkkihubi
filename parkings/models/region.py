from django.contrib.gis.db import models as gis_models
from django.contrib.gis.db.models.functions import Intersection
from django.db import models
from django.db.models import Case, Count, Q, When
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from parkings.models import EnforcementDomain

from .mixins import TimestampedModelMixin, UUIDPrimaryKeyMixin
from .parking_area import ParkingArea


class RegionQuerySet(models.QuerySet):
    def with_parking_count(self, at_time=None):
        time = at_time if at_time else timezone.now()
        valid_parkings_q = (
            Q(parkings__time_start__lte=time) &
            (Q(parkings__time_end__gte=time) | Q(parkings__time_end=None)))
        return self.annotate(
            parking_count=Count(Case(When(valid_parkings_q, then=1))))


class Region(TimestampedModelMixin, UUIDPrimaryKeyMixin):
    name = models.CharField(max_length=200, blank=True, verbose_name=_("name"))
    geom = gis_models.MultiPolygonField(srid=3879, verbose_name=_("geometry"))
    capacity_estimate = models.PositiveIntegerField(
        blank=True, null=True,
        verbose_name=_("capacity estimate"),
    )
    domain = models.ForeignKey(EnforcementDomain, on_delete=models.PROTECT, related_name='regions')

    objects = RegionQuerySet.as_manager()

    class Meta:
        verbose_name = _("region")
        verbose_name_plural = _("regions")

    def __str__(self):
        return self.name or str(_("Unnamed region"))

    def save(self, *args, **kwargs):
        self.capacity_estimate = self.calculate_capacity_estimate()
        if not self.domain_id:
            self.domain = EnforcementDomain.get_default_domain()
        super().save(*args, **kwargs)

    def calculate_capacity_estimate(self):
        """
        Calculate capacity estimate of this region from parking areas.

        :rtype: int
        """
        areas = ParkingArea.objects.all()
        covered_areas = areas.inside_region(self)
        partial_areas = (
            areas.intersecting_region(self).exclude(pk__in=covered_areas)
            .annotate(intsect=Intersection('geom', self.geom)))
        sum_covered = covered_areas.total_estimated_capacity
        sum_partials = sum(
            # Scale the estimated capacity according to ratio of area of
            # the intersection and total area
            int(round(x.estimated_capacity * x.intsect.area / x.geom.area))
            for x in partial_areas)
        return sum_covered + sum_partials
