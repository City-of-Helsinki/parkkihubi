from django.contrib.gis.db import models as gis_models
from django.db import models
from django.utils.translation import gettext_lazy as _

from .constants import GK25FIN_SRID
from .mixins import TimestampedModelMixin


class EnforcementDomain(TimestampedModelMixin):
    code = models.CharField(max_length=10, unique=True, verbose_name=_('code'))
    name = models.CharField(max_length=40, verbose_name=_('name'))
    geom = gis_models.MultiPolygonField(
        srid=GK25FIN_SRID, verbose_name=_('geometry'))

    class Meta:
        ordering = ('code',)

    def __str__(self):
        return str(self.name)

    def __repr__(self):
        return '<{} {!r} {}>'.format(type(self).__name__, self.code, self.name)
