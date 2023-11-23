from datetime import datetime

from django.conf import settings
from django.contrib.gis.db import models as gis_models
from django.contrib.postgres.fields import JSONField
from django.core.serializers.json import DjangoJSONEncoder
from django.db import connections, models, router, transaction
from django.db.models.expressions import RawSQL
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from ..fields import CleaningJsonField
from ..validators import DictListValidator, TextField, TimestampField
from .constants import GK25FIN_SRID
from .enforcement_domain import EnforcementDomain
from .mixins import AnonymizableRegNumQuerySet, TimestampedModelMixin
from .parking import Parking


class PermitAreaQuerySet(models.QuerySet):
    def for_user(self, user):
        return self.filter(allowed_users=user)


class PermitArea(TimestampedModelMixin):
    name = models.CharField(max_length=40, verbose_name=_('name'))
    domain = models.ForeignKey(
        EnforcementDomain, on_delete=models.PROTECT,
        related_name='permit_areas')
    identifier = models.CharField(max_length=10, verbose_name=_('identifier'))
    geom = gis_models.MultiPolygonField(
        srid=GK25FIN_SRID, verbose_name=_('geometry'))
    allowed_users = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        verbose_name=_("allowed users"),
        related_name="allowed_permit_areas",
        help_text=_("Users who are allowed to create permits to this area."),
    )

    objects = PermitAreaQuerySet.as_manager()

    class Meta:
        unique_together = [('domain', 'identifier')]
        ordering = ('identifier',)

    def __str__(self):
        return '{}/{}: {}'.format(self.domain.code, self.identifier, self.name)

    @classmethod
    def get_identifier_map(cls, domain, using="default"):
        areas = cls.objects.using(using).filter(domain=domain)
        return dict(areas.values_list("identifier", "id"))


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

    def all_items_end_before(self, time: datetime) -> "PermitQuerySet":
        """
        Filter to permits whose all lookup items end before given time.

        The returned queryset can be used to find permits that are no
        longer valid at the given time and therefore can be anonymized.

        The returned queryset is a subset of the queryset from which it
        was called.

        Note: The returned queryset can have permits that don't have any
        lookup items at all. (By definition "all" lookup items of those
        permits end before the given time, since they have none.)

        Note 2: The returned queryset can have permits that have subject
        items that are still valid at the given time, but their
        effective validity is limited by the end time of the area items,
        and therefore they still can be anonymized.
        """
        # Use a subquery to find the permits which have any lookup item
        # that is still valid at the given time.  The subquery is then
        # used to exclude those permits from the queryset.  This way the
        # returned queryset contains only permits that have no valid
        # lookup items at the given time.
        quote = connections[self.db].ops.quote_name
        excluded_permit_ids_sql = RawSQL(
            """
            SELECT DISTINCT(permit_id)
            FROM {item_table} AS pli
            WHERE pli.end_time >= %s
            """.format(
                item_table=quote(PermitLookupItem._meta.db_table),
            ),
            (time,)
        )
        return self.exclude(pk__in=excluded_permit_ids_sql)

    def unanonymized(self) -> "PermitQuerySet":
        """
        Filter to permits that have not been fully anonymized.
        """
        subjects = PermitSubjectItem.objects.unanonymized()
        permits_which_have_data = subjects.values("permit")
        return self.filter(id__in=permits_which_have_data)

    @transaction.atomic
    def anonymize(self, batch_size=1000):
        """
        Anonymize registration numbers of the permits in this queryset.
        """
        count = 0
        all_ids = self.order_by("id").values_list("id", flat=True)
        for start_idx in range(0, len(all_ids), batch_size):
            ids = all_ids[start_idx:start_idx + batch_size]
            batch = self.model.objects.filter(id__in=ids).order_by()
            updated_permits = []
            for permit in batch.only("id", "subjects"):
                permit.anonymize_subjects()
                updated_permits.append(permit)
            batch.bulk_update(updated_permits, ["subjects"], batch_size)
            count += len(updated_permits)
            lookup_items = PermitLookupItem.objects.filter(permit_id__in=ids)
            assert isinstance(lookup_items, PermitLookupItemQuerySet)
            lookup_items.anonymize()
            subjects = PermitSubjectItem.objects.filter(permit_id__in=ids)
            assert isinstance(subjects, PermitSubjectItemQuerySet)
            subjects.anonymize()
        return count

    def bulk_create(self, permits, *args, **kwargs):
        for permit in permits:
            assert isinstance(permit, Permit)
            permit.full_clean()

        area_ids_cache = {}

        with transaction.atomic(using=self.db, savepoint=False):
            created_permits = super().bulk_create(permits, *args, **kwargs)
            for permit in created_permits:
                area_ids = area_ids_cache.get(permit.domain_id) or (
                    area_ids_cache.setdefault(
                        permit.domain_id,
                        PermitArea.get_identifier_map(permit.domain, self.db)))
                permit._create_all_items(area_ids, using=self.db, is_new=True)
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
    properties = JSONField(blank=True, null=True, encoder=DjangoJSONEncoder, verbose_name=_("properties"))

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

    def anonymize_subjects(self):
        """
        Anonymize registration numbers of the subjects of this permit.

        This method does not save the permit.
        """
        empty_reg_num = {"registration_number": ""}
        self.subjects = [{**x, **empty_reg_num} for x in self.subjects]

    def save(self, using=None, *args, **kwargs):
        self.full_clean()
        is_new = (self.id is None)
        using = using or router.db_for_write(type(self), instance=self)
        with transaction.atomic(using=using, savepoint=False):
            super(Permit, self).save(using=using, *args, **kwargs)
            self._create_all_items(using=using, is_new=is_new)

    def _create_all_items(self, area_ids=None, using="default", is_new=False):
        if area_ids is None:
            area_ids = PermitArea.get_identifier_map(self.domain, using)
        if not is_new:
            self.lookup_items.all().using(using).delete()
            self.subject_items.all().using(using).delete()
            self.area_items.all().using(using).delete()
        subject_items = self._create_subject_items(using)
        area_items = self._create_area_items(using, area_ids)
        lookup_items = self._make_lookup_items(area_items, subject_items)
        PermitLookupItem.objects.using(using).bulk_create(lookup_items)

    def _create_subject_items(self, using):
        subject_items = [
            PermitSubjectItem(
                permit_id=self.id,
                registration_number=subject["registration_number"],
                start_time=subject["start_time"],
                end_time=subject["end_time"],
            )
            for subject in self.subjects
        ]
        PermitSubjectItem.objects.using(using).bulk_create(subject_items)
        return subject_items

    def _create_area_items(self, using, area_ids):
        area_items = [
            PermitAreaItem(
                permit_id=self.id,
                area_id=area_ids[area["area"]],
                start_time=area["start_time"],
                end_time=area["end_time"],
            )
            for area in self.areas
        ]
        PermitAreaItem.objects.using(using).bulk_create(area_items)
        return area_items

    def _make_lookup_items(self, area_items, subject_items):
        for area_item in area_items:
            for subject_item in subject_items:
                # Calculate intersection of the area and subject ranges.
                #
                # An illustration of the area range [A_start,A_end],
                # subject range [S_start,S_end], and their intersection
                # [I_start,I_end].
                #
                # The formulas for intersection endpoints are:
                #   I_start = max(S_start, A_start)
                #   I_end = min(S_end, A_end)
                #
                #          S_start      S_end
                #          |------------|
                #              &
                #  A_start          A_end
                #  |----------------|
                #              |
                #              V
                #          I_start  I_end
                #          |--------|
                #
                start_time = max(subject_item.start_time, area_item.start_time)
                end_time = min(subject_item.end_time, area_item.end_time)

                if start_time > end_time:  # Distinct ranges
                    continue
                yield PermitLookupItem(
                    permit=self,
                    subject_item=subject_item,
                    area_item=area_item,
                    registration_number=Parking.normalize_reg_num(
                        subject_item.registration_number),
                    area=area_item.area,
                    start_time=start_time,
                    end_time=end_time
                )


class PermitSubjectItemQuerySet(AnonymizableRegNumQuerySet):
    pass


class PermitSubjectItem(models.Model):
    permit = models.ForeignKey(
        Permit, on_delete=models.CASCADE, related_name='subject_items')
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    registration_number = models.CharField(max_length=20)

    objects = PermitSubjectItemQuerySet.as_manager()

    def __str__(self):
        return 'Permit {p} Subject {reg_num} ({start_time}-{end_time})'.format(
            p=self.permit.id,
            reg_num=self.registration_number,
            start_time=self.start_time,
            end_time=self.end_time)


class PermitAreaItem(models.Model):
    permit = models.ForeignKey(
        Permit, on_delete=models.CASCADE, related_name='area_items')
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    area = models.ForeignKey(PermitArea, on_delete=models.PROTECT)

    def __str__(self):
        return 'Permit {p} Area {area} ({start_time}-{end_time})'.format(
            p=self.permit.id,
            area=self.area.identifier,
            start_time=self.start_time,
            end_time=self.end_time)


class PermitLookupItemQuerySet(AnonymizableRegNumQuerySet, models.QuerySet):
    def active(self):
        return self.filter(permit__series__active=True)

    def by_time(self, timestamp):
        return self.filter(start_time__lte=timestamp, end_time__gte=timestamp)

    def by_subject(self, registration_number):
        normalized_reg_num = Parking.normalize_reg_num(registration_number)
        return self.filter(registration_number=normalized_reg_num)

    def by_area(self, area):
        return self.filter(area=area)

    def ends_before(self, time):
        return self.filter(end_time__lt=time)


class PermitLookupItem(models.Model):
    permit = models.ForeignKey(
        Permit, related_name="lookup_items", on_delete=models.CASCADE)
    subject_item = models.ForeignKey(
        PermitSubjectItem, related_name="lookup_items", on_delete=models.CASCADE,
        null=True, blank=True)
    area_item = models.ForeignKey(
        PermitAreaItem, related_name="lookup_items", on_delete=models.CASCADE,
        null=True, blank=True)
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
