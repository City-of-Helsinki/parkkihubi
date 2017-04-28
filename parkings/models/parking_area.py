from django.contrib.gis.db import models
from django.utils.translation import ugettext_lazy as _

from parkings.models.mixins import TimestampedModelMixin, UUIDPrimaryKeyMixin


class ParkingArea(TimestampedModelMixin, UUIDPrimaryKeyMixin):
    # This is for whatever ID the external system that this parking lot was
    # imported from has assigned to this lot. There is no guarantee that it will
    # always be a number or that it will be unique, especially if multiple
    # sources are to be used, but for now this should be enough to at least fail
    # early if there are inconsistencies in the external system.
    origin_id = models.CharField(
        verbose_name=_('external ID'),
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
        verbose_name=_('capasity estimate'),
        null=True,
        blank=True,
    )

    class Meta:
        verbose_name = _('parking area')
        verbose_name_plural = _('parking areas')

    def __str__(self):
        return 'Parking Area %s' % str(self.origin_id)
