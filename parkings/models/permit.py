from itertools import chain

from django.conf import settings
from django.contrib.gis.db import models as gis_models
from django.db import models, router, transaction
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from ..fields import CleaningJsonField
from ..validators import DictListValidator, TextField, TimestampField
from .constants import GK25FIN_SRID
from .enforcement_domain import EnforcementDomain
from .mixins import TimestampedModelMixin
from .parking import Parking


class PermitArea(TimestampedModelMixin):
    name = models.CharField(max_length=40, verbose_name=_('name'))
    domain = models.ForeignKey(
        EnforcementDomain, on_delete=models.PROTECT,
        related_name='permit_areas')
    identifier = models.CharField(max_length=10, verbose_name=_('identifier'))
    geom = gis_models.MultiPolygonField(
        srid=GK25FIN_SRID, verbose_name=_('geometry'))
    permitted_user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, verbose_name=_("permitted_user"))

    class Meta:
        unique_together = [('domain', 'identifier')]
        ordering = ('identifier',)

    def __str__(self):
        return '{}/{}: {}'.format(self.domain.code, self.identifier, self.name)


class PermitSeriesQuerySet(models.QuerySet):
    def active(self):
        return self.filter(active=True)

    def latest_active(self):
        return self.active().order_by('-modified_at').first()

    def prunable(self, time_limit=None):
        limit = time_limit or (
            timezone.now() - settings.PARKKIHUBI_PERMITS_PRUNABLE_AFTER)
        return self.filter(created_at__lt=limit, active=False)


class PermitSeries(TimestampedModelMixin, models.Model):
    active = models.BooleanField(default=False)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, verbose_name=_("owner"))
    objects = PermitSeriesQuerySet.as_manager()

    class Meta:
        ordering = ('created_at', 'id')
        verbose_name = _("permit series")
        verbose_name_plural = _("permit series")

    @classmethod
    def delete_prunable_series(cls, time_limit=None):
        prunable = cls.objects.prunable(time_limit)
        Permit.objects.filter(series__in=prunable).delete()
        prunable.delete()

    def __str__(self):
        return str(self.id)


class PermitQuerySet(models.QuerySet):
    def active(self):
        return self.filter(series__active=True)

    def by_time(self, timestamp):
        lookup_items = PermitLookupItem.objects.by_time(timestamp)
        return self.filter(lookup_items__in=lookup_items).distinct()

    def by_subject(self, registration_number):
        lookup_items = PermitLookupItem.objects.by_subject(registration_number)
        return self.filter(lookup_items__in=lookup_items).distinct()

    def by_area(self, area):
        lookup_items = PermitLookupItem.objects.by_area(area)
        return self.filter(lookup_items__in=lookup_items).distinct()

    def bulk_create(self, permits, *args, **kwargs):
        for permit in permits:
            assert isinstance(permit, Permit)
            permit.full_clean()

        with transaction.atomic(using=self.db, savepoint=False):
            created_permits = super().bulk_create(permits, *args, **kwargs)
            PermitLookupItem.objects.using(self.db).bulk_create(
                chain(*(x._make_lookup_items() for x in created_permits)))
            return created_permits


class Permit(TimestampedModelMixin, models.Model):
    domain = models.ForeignKey(
        EnforcementDomain, on_delete=models.PROTECT,
        related_name='permits')
    series = models.ForeignKey(PermitSeries, on_delete=models.PROTECT)
    external_id = models.CharField(max_length=50, null=True, blank=True)
    subjects = CleaningJsonField(blank=True, validators=[DictListValidator({
        'start_time': TimestampField(),
        'end_time': TimestampField(),
        'registration_number': TextField(max_length=20),
    })])
    areas = CleaningJsonField(blank=True, validators=[DictListValidator({
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
        return 'Permit {id} ({series}{active}/{external_id} {dom})'.format(
            id=self.id,
            dom=self.domain.code,
            series=self.series,
            active='*' if self.series.active else '',
            external_id=self.external_id)

    def save(self, using=None, *args, **kwargs):
        self.full_clean()
        using = using or router.db_for_write(type(self), instance=self)
        with transaction.atomic(using=using, savepoint=False):
            super(Permit, self).save(using=using, *args, **kwargs)
            self.lookup_items.all().using(using).delete()
            new_lookup_items = self._make_lookup_items()
            PermitLookupItem.objects.using(using).bulk_create(new_lookup_items)

    def _make_lookup_items(self):
        for area in self.areas:
            for subject in self.subjects:
                max_start_time = max(subject['start_time'], area['start_time'])
                min_end_time = min(subject['end_time'], area['end_time'])

                if max_start_time >= min_end_time:
                    continue
                yield PermitLookupItem(
                    permit=self,
                    registration_number=Parking.normalize_reg_num(
                        subject['registration_number']),
                    area=PermitArea.objects.get(identifier=area['area'], domain=self.domain),
                    start_time=max_start_time,
                    end_time=min_end_time
                )


class PermitLookupItemQuerySet(models.QuerySet):
    def active(self):
        return self.filter(permit__series__active=True)

    def by_time(self, timestamp):
        return self.filter(start_time__lte=timestamp, end_time__gte=timestamp)

    def by_subject(self, registration_number):
        normalized_reg_num = Parking.normalize_reg_num(registration_number)
        return self.filter(registration_number=normalized_reg_num)

    def by_area(self, area):
        return self.filter(area=area)


class PermitLookupItem(models.Model):
    permit = models.ForeignKey(
        Permit, related_name="lookup_items", on_delete=models.CASCADE)
    registration_number = models.CharField(max_length=20)
    area = models.ForeignKey(PermitArea, on_delete=models.PROTECT, default=None, null=True, blank=True)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()

    objects = PermitLookupItemQuerySet.as_manager()

    class Meta:
        indexes = [
            models.Index(fields=[
                'registration_number', 'start_time', 'end_time',
                'area', 'permit']),
        ]
        ordering = ('registration_number', 'start_time', 'end_time')

    def __str__(self):
        return (
            '{start_time:%Y-%m-%d %H:%M} -- {end_time:%Y-%m-%d %H:%M} / '
            '{registration_number} / {area}'
        ).format(
            start_time=self.start_time, end_time=self.end_time,
            registration_number=self.registration_number,
            area=self.area.identifier)
