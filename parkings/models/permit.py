from django.contrib.gis.db import models as gis_models
from django.contrib.postgres.fields import JSONField
from django.core.exceptions import ValidationError
from django.db import models, transaction
from django.utils.translation import gettext_lazy as _

from .constants import GK25FIN_SRID
from .mixins import TimestampedModelMixin, UUIDPrimaryKeyMixin


class PermitArea(TimestampedModelMixin, UUIDPrimaryKeyMixin):
    name = models.CharField(max_length=40, verbose_name=_('name'))
    identifier = models.CharField(max_length=10, verbose_name=_('identifier'))
    geom = gis_models.MultiPolygonField(
        srid=GK25FIN_SRID, verbose_name=_('geometry'))

    class Meta:
        ordering = ('identifier',)

    def __str__(self):
        return '{}: {}'.format(self.identifier, self.name)


class PermitSeries(TimestampedModelMixin, models.Model):
    active = models.BooleanField(default=False)

    class Meta:
        ordering = ('created_at', 'id')

    def __str__(self):
        return str(self.id)


class PermitQuerySet(models.QuerySet):
    def active(self):
        return self.filter(series__active=True)

    def by_time(self, timestamp):
        return self.filter(
            cache_items__in=PermitCacheItem.objects.by_time(timestamp))

    def by_subject(self, registration_number):
        return self.filter(
            cache_items__in=PermitCacheItem.objects.by_subject(registration_number)).distinct()

    def by_area(self, area_identifier):
        return self.filter(
            cache_items__in=PermitCacheItem.objects.by_area(area_identifier))


class Permit(TimestampedModelMixin, models.Model):
    series = models.ForeignKey(PermitSeries, on_delete=models.PROTECT)
    external_id = models.CharField(max_length=50, null=True, blank=True)
    subjects = JSONField()
    areas = JSONField()

    objects = PermitQuerySet.as_manager()

    class Meta:
        unique_together = [('series', 'external_id')]
        indexes = [
            models.Index(fields=['series', 'id']),
        ]
        ordering = ('series', 'id')

    def __str__(self):
        return ('Permit {}'.format(self.id))

    def clean(self):
        super(Permit, self).clean()
        for subject in self.subjects:
            if (
                'start_time' not in subject
                or 'end_time' not in subject
                or 'registration_number' not in subject
            ):
                raise ValidationError({'subjects': _('Subjects is not valid')})
        for area in self.areas:
            if (
                'start_time' not in area
                or 'end_time' not in area
                or 'area' not in area
            ):
                raise ValidationError({'areas': _('Areas is not valid')})

    def save(self, *args, **kwargs):
        self.clean()
        with transaction.atomic():
            super(Permit, self).save(*args, **kwargs)
            self._create_cache_items()

    def _create_cache_items(self):
        """
        Create the combination of subject and areas for each permit instance
        for fast lookup. Save it as the instance of PermitCacheItem.
        """
        self.cache_items.all().delete()
        for area in self.areas:
            for subject in self.subjects:
                max_start_time = max(subject['start_time'], area['start_time'])
                min_end_time = min(subject['end_time'], area['end_time'])

                if max_start_time >= min_end_time:
                    continue
                self.cache_items.create(
                    permit=self,
                    registration_number=subject['registration_number'],
                    area_identifier=area['area'],
                    start_time=max_start_time,
                    end_time=min_end_time
                )


class PermitCacheItemQuerySet(models.QuerySet):
    def by_time(self, timestamp):
        return self.filter(start_time__lte=timestamp, end_time__gte=timestamp)

    def by_subject(self, registration_number):
        return self.filter(registration_number=registration_number)

    def by_area(self, area_identifier):
        return self.filter(area_identifier=area_identifier)


class PermitCacheItem(models.Model):
    permit = models.ForeignKey(Permit, related_name="cache_items")
    registration_number = models.CharField(max_length=30)
    area_identifier = models.CharField(max_length=10)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()

    objects = PermitCacheItemQuerySet.as_manager()

    def __str__(self):
        return (
            '{start_time:%Y-%m-%d %H:%M} -- {end_time:%Y-%m-%d %H:%M} / '
            '{registration_number} / {area_identifier}'
        ).format(
            start_time=self.start_time, end_time=self.end_time,
            registration_number=self.registration_number,
            area_identifier=self.area_identifier)
