import uuid

from django.contrib.gis.db import models
from django.utils.translation import ugettext_lazy as _


class TimestampedModelMixin(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("time created"))
    modified_at = models.DateTimeField(auto_now=True, verbose_name=_("time modified"))

    class Meta:
        abstract = True


class UUIDPrimaryKeyMixin(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    class Meta:
        abstract = True
