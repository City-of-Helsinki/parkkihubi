from django.contrib.gis.db import models
from django.utils.translation import ugettext_lazy as _

from parkings.models.mixins import TimestampedModelMixin, UUIDPrimaryKeyMixin


class Address(TimestampedModelMixin, UUIDPrimaryKeyMixin):
    city = models.CharField(verbose_name=_("city"), blank=True, max_length=80)
    postal_code = models.CharField(verbose_name=_("postal code"), blank=True, max_length=20)
    street = models.CharField(verbose_name=_("street address"), blank=True, max_length=128)
