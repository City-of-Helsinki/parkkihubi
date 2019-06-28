from django.conf import settings
from django.contrib.gis.db import models as gis_models
from django.db import models, transaction
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from ..fields import CleaningJsonField
from ..validators import DictListValidator, TextField, TimestampField
from .constants import GK25FIN_SRID
from .mixins import TimestampedModelMixin, UUIDPrimaryKeyMixin
from .parking import Parking


class PermitArea(TimestampedModelMixin, UUIDPrimaryKeyMixin):
    name = models.CharField(max_length=40, verbose_name=_('name'))
    identifier = models.CharField(
        max_length=10, unique=True, verbose_name=_('identifier'))
    geom = gis_models.MultiPolygonField(
        srid=GK25FIN_SRID, verbose_name=_('geometry'))

    class Meta:
        ordering = ('identifier',)

    def __str__(self):
        return '{}: {}'.format(self.identifier, self.name)


class PermitSeriesQuerySet(models.QuerySet):
    def active(self):
        return self.filter(active=True)

    def latest_active(self):
        return self.active().order_by('-modified_at').first()

    def prunable(self):
        pruneable_after_date = timezone.now() - settings.PARKKIHUBI_PERMITS_PRUNABLE_AFTER_DAYS
        return self.filter(created_at__lt=pruneable_after_date, active=False)


class PermitSeries(TimestampedModelMixin, models.Model):
    active = models.BooleanField(default=False)

    objects = PermitSeriesQuerySet.as_manager()

    class Meta:
        ordering = ('created_at', 'id')

    def __str__(self):
        return str(self.id)


class PermitQuerySet(models.QuerySet):
    def active(self):
        return self.filter(series__active=True)

    def by_time(self, timestamp):
        cache_items = PermitCacheItem.objects.by_time(timestamp)
        return self.filter(cache_items__in=cache_items).distinct()

    def by_subject(self, registration_number):
        cache_items = PermitCacheItem.objects.by_registration_number(
            Parking.normalize_reg_num(registration_number))
        return self.filter(cache_items__in=cache_items).distinct()

    def by_area(self, area_identifier):
        cache_items = PermitCacheItem.objects.by_area(area_identifier)
        return self.filter(cache_items__in=cache_items).distinct()

    def bulk_create(self, permits, *args, **kwargs):
        with transaction.atomic(using=self.db, savepoint=False):
            created_permits = super().bulk_create(permits, *args, **kwargs)
            cache_items = []
            for permit in created_permits:
                assert isinstance(permit, Permit)
                cache_items.extend(permit._make_cache_items())
            PermitCacheItem.objects.using(self.db).bulk_create(cache_items)
            return created_permits


class Permit(TimestampedModelMixin, models.Model):
    series = models.ForeignKey(PermitSeries, on_delete=models.PROTECT)
    external_id = models.CharField(max_length=50, null=True, blank=True)
    subjects = CleaningJsonField(validators=[DictListValidator({
        'start_time': TimestampField(),
        'end_time': TimestampField(),
        'registration_number': TextField(max_length=20),
    })])
    areas = CleaningJsonField(validators=[DictListValidator({
        'start_time': TimestampField(),
        'end_time': TimestampField(),
        'area': TextField(max_length=10),
    })])

    objects = PermitQuerySet.as_manager()

    class Meta:
        unique_together = [('series', 'external_id')]
        indexes = [
            models.Index(fields=['series', 'id']),
        ]
        ordering = ('series', 'id')

    def __str__(self):
        return ('Permit {}'.format(self.id))

    def save(self, *args, **kwargs):
        self.full_clean()
        with transaction.atomic():
            super(Permit, self).save(*args, **kwargs)
            self._update_cache_items()

    def _update_cache_items(self):
        self.cache_items.all().delete()
        PermitCacheItem.objects.bulk_create(self._make_cache_items())

    def _make_cache_items(self):
        for area in self.areas:
            for subject in self.subjects:
                max_start_time = max(subject['start_time'], area['start_time'])
                min_end_time = min(subject['end_time'], area['end_time'])

                if max_start_time >= min_end_time:
                    continue
                yield PermitCacheItem(
                    permit=self,
                    registration_number=Parking.normalize_reg_num(
                        subject['registration_number']),
                    area_identifier=area['area'],
                    start_time=max_start_time,
                    end_time=min_end_time
                )


class PermitCacheItemQuerySet(models.QuerySet):
    def by_time(self, timestamp):
        return self.filter(start_time__lte=timestamp, end_time__gte=timestamp)

    def by_registration_number(self, registration_number):
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
