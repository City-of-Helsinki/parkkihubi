from django.conf import settings
from django.contrib.gis.db import models
from django.utils.translation import gettext_lazy as _

from parkings.models import EnforcementDomain
from parkings.models.mixins import TimestampedModelMixin, UUIDPrimaryKeyMixin


class Monitor(TimestampedModelMixin, UUIDPrimaryKeyMixin):
    """
    A person who monitors through the Monitoring API.
    """
    name = models.CharField(verbose_name=_("name"), max_length=80)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, verbose_name=_("user")
    )
    domain = models.ForeignKey(
        EnforcementDomain,
        on_delete=models.PROTECT,
        help_text=_("The enforcement domain user can monitor"),
    )

    class Meta:
        verbose_name = _("monitor")
        verbose_name_plural = _("monitors")

    def __str__(self):
        return self.name
