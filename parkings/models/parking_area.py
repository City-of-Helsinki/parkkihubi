from django.contrib.gis.db import models
from django.contrib.gis.db.models.functions import Area
from django.db.models import Func, Sum
from django.utils.translation import ugettext_lazy as _

from parkings.models.mixins import TimestampedModelMixin, UUIDPrimaryKeyMixin

from .enforcement_domain import EnforcementDomain

# Estimated number of parking spots per square meter (m^2)
PARKING_SPOTS_PER_SQ_M = 0.07328


class Round(Func):
    """
    Function for rounding in SQL using Django ORM.
    """
    function = 'ROUND'


class ParkingAreaQuerySet(models.QuerySet):
    def inside_region(self, region):
        """
        Filter to parking areas which are inside given region.

        :type region: .region.Region
        :rtype: ParkingAreaQuerySet
        """
        return self.filter(geom__coveredby=region.geom)

    def intersecting_region(self, region):
        """
        Filter to parking areas which intersect with given region.

        :type region: .region.Region
        :rtype: ParkingAreaQuerySet
        """
        return self.filter(geom__intersects=region.geom)

    @property
    def total_estimated_capacity(self):
        """
        Estimated number of parking spots in this queryset.

        This is the sum of `parking_area.estimated_capacity` of each
        `parking_area` in this queryset.  The value is calculated in the
        database to make it faster compared to calculating the sum in
        Python.

        :rtype: int
        """
        defined_qs = self.exclude(capacity_estimate=None)
        undefined_qs = self.filter(capacity_estimate=None)
        total_defined = defined_qs.sum_of_capacity_estimates or 0
        total_by_area = undefined_qs.estimate_total_capacity_by_areas()
        return total_defined + total_by_area

    @property
    def sum_of_capacity_estimates(self):
        return self.aggregate(val=Sum('capacity_estimate'))['val']

    def estimate_total_capacity_by_areas(self):
        spots = (
            self.annotate(spots=Round(PARKING_SPOTS_PER_SQ_M * Area('geom')))
            .aggregate(val=Sum('spots')))['val']
        return int(spots.sq_m) if spots else 0


class ParkingArea(TimestampedModelMixin, UUIDPrimaryKeyMixin):
    domain = models.ForeignKey(EnforcementDomain, on_delete=models.PROTECT,
                               related_name='parking_areas')

    # This is for whatever ID the external system that this parking lot was
    # imported from has assigned to this lot. There is no guarantee that it will
    # always be a number or that it will be unique, especially if multiple
    # sources are to be used, but for now this should be enough to at least fail
    # early if there are inconsistencies in the external system.
    origin_id = models.CharField(
        verbose_name=_('origin ID'),
        max_length=32,
        db_index=True,
        unique=True,
    )

    # This represents a whole parking area, such as a street or parking lot, and
    # as such it can contain multiple polygons.
    # There are areas with only a single polygon, but creating a special case for
    # those would probably increase complexity.
    geom = models.MultiPolygonField(
        verbose_name=_('geometry'),
        srid=3879,
    )

    # This is a rough capacity estimate of how many cars might fit into the
    # parking area.
    capacity_estimate = models.PositiveSmallIntegerField(
        verbose_name=_('capacity estimate'),
        null=True,
        blank=True,
    )

    # General purpose name field. Most likely will have the street name.
    name = models.CharField(
        verbose_name=_("name"),
        max_length=200,
        blank=True,
        default="",
    )

    objects = ParkingAreaQuerySet.as_manager()

    class Meta:
        verbose_name = _('parking area')
        verbose_name_plural = _('parking areas')

    def __str__(self):
        return 'Parking Area %s' % str(self.origin_id)

    def save(self, *args, **kwargs):
        if not self.domain_id:
            self.domain = EnforcementDomain.get_default_domain()
        super().save(*args, **kwargs)

    @property
    def estimated_capacity(self):
        """
        Estimated number of parking spots in this parking area.

        If there is a capacity estimate specified for this area in the
        `capacity_estimate` field, return it, otherwise return a
        capacity estimate based on the area (m^2) of this parking area.

        :rtype: int
        """
        return (
            self.capacity_estimate if self.capacity_estimate is not None
            else self.estimate_capacity_by_area())

    def estimate_capacity_by_area(self):
        """
        Estimate number of parking spots in this parking area by m^2.

        :rtype: int
        """
        assert self.geom.srs.units == (1.0, 'metre')
        return int(round(self.geom.area * PARKING_SPOTS_PER_SQ_M))
