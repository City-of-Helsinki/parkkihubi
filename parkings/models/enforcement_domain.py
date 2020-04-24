from django.conf import settings
from django.contrib.gis.db import models as gis_models
from django.db import models
from django.utils.translation import gettext_lazy as _

from .constants import GK25FIN_SRID
from .mixins import TimestampedModelMixin, UUIDPrimaryKeyMixin


class EnforcementDomain(TimestampedModelMixin):
    code = models.CharField(max_length=10, unique=True, verbose_name=_('code'))
    name = models.CharField(max_length=40, verbose_name=_('name'))
    geom = gis_models.MultiPolygonField(srid=GK25FIN_SRID, verbose_name=_('geometry'), null=True)

    class Meta:
        ordering = ('code',)

    def __str__(self):
        return str(self.name)

    def __repr__(self):
        return '<{} {!r} {}>'.format(type(self).__name__, self.code, self.name)

    @classmethod
    def get_default_domain(cls):
        (name, code) = settings.DEFAULT_ENFORCEMENT_DOMAIN
        return cls.objects.get_or_create(
            code=code, defaults={"name": name})[0]

    @classmethod
    def get_default_domain_code(cls):
        return settings.DEFAULT_ENFORCEMENT_DOMAIN[1]


class Enforcer(TimestampedModelMixin, UUIDPrimaryKeyMixin):
    name = models.CharField(verbose_name=_("name"), max_length=80)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, verbose_name=_("user"))
    enforced_domain = models.ForeignKey(
        EnforcementDomain, verbose_name=_("enforced domain"), on_delete=models.PROTECT,
        help_text=_("The enforcement domain enforced by this enforcer"))

    class Meta:
        verbose_name = _("enforcer")
        verbose_name_plural = _("enforcers")

    def __str__(self):
        return self.name
