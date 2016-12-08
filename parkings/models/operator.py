from django.contrib.auth.models import User
from django.contrib.gis.db import models
from django.utils.translation import ugettext_lazy as _

from parkings.models.mixins import TimestampedModelMixin, UUIDPrimaryKeyMixin


class Operator(TimestampedModelMixin, UUIDPrimaryKeyMixin):
    name = models.CharField(verbose_name=_("name"), max_length=80)
    user = models.OneToOneField(User, on_delete=models.PROTECT, verbose_name=_("user"))

    def __str__(self):
        return self.name
