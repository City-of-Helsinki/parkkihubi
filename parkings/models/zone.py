from django.contrib.gis.db import models as gis_models
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.translation import ugettext_lazy as _

from .constants import GK25FIN_SRID
from .mixins import TimestampedModelMixin


class PaymentZone(TimestampedModelMixin):
    number = models.IntegerField(
        unique=True, validators=[MinValueValidator(1), MaxValueValidator(3)],
        verbose_name=_('zone number'))
    name = models.CharField(max_length=40, verbose_name=_('name'))
    geom = gis_models.MultiPolygonField(
        srid=GK25FIN_SRID, verbose_name=_('geometry'))

    def __str__(self):
        return self.name
