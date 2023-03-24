from django.contrib.gis.db import models
from django.contrib.gis.db.models.functions import Distance
from django.db import connections, router, transaction
from django.utils import timezone
from django.utils.timezone import localtime, now
from django.utils.translation import ugettext_lazy as _

from parkings.models.mixins import TimestampedModelMixin, UUIDPrimaryKeyMixin
from parkings.models.operator import Operator
from parkings.models.parking_area import ParkingArea
from parkings.models.zone import PaymentZone
from parkings.utils.sanitizing import sanitize_registration_number

from ..utils.model_fields import with_model_field_modifications
from ..utils.querysets import make_batches
from .enforcement_domain import EnforcementDomain
from .mixins import AnonymizableRegNumQuerySet
from .parking_terminal import ParkingTerminal
from .region import Region

Q = models.Q


class ParkingQuerySet(AnonymizableRegNumQuerySet, models.QuerySet):
    def valid_at(self, time):
        """
        Filter to parkings which are valid at given time.

        :type time: datetime.datetime
        :rtype: ParkingQuerySet
        """
        return self.starts_before(time).ends_after(time)

    def starts_before(self, time):
        return self.filter(time_start__lte=time)

    def ends_after(self, time):
        return self.filter(Q(time_end__gte=time) | Q(time_end=None))

    def ends_before(self, time):
        return self.exclude(time_end=None).filter(time_end__lt=time)

    def anonymize(self):  # override to also anonymize normalized_reg_num
        return self.update(registration_number="", normalized_reg_num="")

    def archive(
        self,
        batch_size=1000,
        limit=None,
        pre_archive_callback=(lambda batch, total: None),
        post_archive_callback=(lambda batch, total: None),
        dry_run=False,
    ):
        if issubclass(self.model, ArchivedParking):
            return 0  # Nothing archived, since was already archived
        if limit and batch_size > limit:
            batch_size = limit
        total_archived = 0
        for batch in make_batches(self, batch_size, "time_end"):
            if limit and total_archived + batch_size > limit:
                remaining = limit - total_archived
                batch = batch[:remaining]
            pre_archive_callback(batch, total_archived)
            if not dry_run:
                (_archived, count) = ArchivedParking.archive_in_bulk(batch)
            else:
                count = batch.count()
            total_archived += count
            post_archive_callback(batch, total_archived)
            if limit and total_archived >= limit:
                break
        return total_archived

    def registration_number_like(self, registration_number):
        """
        Filter to parkings having registration number like the given value.

        :type registration_number: str
        :rtype: ParkingQuerySet
        """
        normalized_reg_num = Parking.normalize_reg_num(registration_number)
        return self.filter(normalized_reg_num=normalized_reg_num)


class AbstractParking(TimestampedModelMixin, UUIDPrimaryKeyMixin):
    VALID = 'valid'
    NOT_VALID = 'not_valid'

    region = models.ForeignKey(
        Region, null=True, blank=True, on_delete=models.SET_NULL,
        verbose_name=_("region"),
    )
    parking_area = models.ForeignKey(
        ParkingArea, on_delete=models.SET_NULL, verbose_name=_("parking area"), null=True,
        blank=True,
    )
    terminal_number = models.CharField(
        max_length=50,  blank=True,
        verbose_name=_("terminal number"),
    )
    terminal = models.ForeignKey(
        ParkingTerminal, null=True, blank=True,
        on_delete=models.SET_NULL,
        verbose_name=_("terminal"),
    )
    location = models.PointField(verbose_name=_("location"), null=True, blank=True)
    operator = models.ForeignKey(
        Operator, on_delete=models.PROTECT, verbose_name=_("operator")
    )
    registration_number = models.CharField(max_length=20, db_index=True, verbose_name=_("registration number"))
    normalized_reg_num = models.CharField(
        max_length=20, db_index=True,
        verbose_name=_("normalized registration number"),
    )
    time_start = models.DateTimeField(
        verbose_name=_("parking start time"), db_index=True,
    )
    time_end = models.DateTimeField(
        verbose_name=_("parking end time"), db_index=True, null=True, blank=True,
    )
    domain = models.ForeignKey(
        EnforcementDomain, on_delete=models.PROTECT,
        null=True,)
    zone = models.ForeignKey(
        PaymentZone, on_delete=models.PROTECT,
        verbose_name=_("PaymentZone"), null=True, blank=True)
    is_disc_parking = models.BooleanField(verbose_name=_("disc parking"), default=False)

    objects = ParkingQuerySet.as_manager()

    class Meta:
        abstract = True

    def __str__(self):
        start = localtime(self.time_start).replace(tzinfo=None)

        if self.time_end is None:
            return "%s -> (%s)" % (start, self.registration_number)

        if self.time_start.date() == self.time_end.date():
            end = localtime(self.time_end).time().replace(tzinfo=None)
        else:
            end = localtime(self.time_end).replace(tzinfo=None)

        return "%s -> %s (%s)" % (start, end, self.registration_number)


class Parking(AbstractParking):
    class Meta:
        verbose_name = _("parking")
        verbose_name_plural = _("parkings")
        default_related_name = "parkings"

    def archive(self):
        archived_parking = self.make_archived_parking()
        with transaction.atomic():
            archived_parking.save()
            self.delete()
            return archived_parking

    def make_archived_parking(self):
        fields = [field.name for field in self._meta.fields]
        values = {field: getattr(self, field) for field in fields}
        return ArchivedParking(**values)

    def get_state(self):
        current_timestamp = now()

        if self.time_start > current_timestamp:
            return Parking.NOT_VALID

        if self.time_end and self.time_end < current_timestamp:
            return Parking.NOT_VALID

        return Parking.VALID

    def get_region(self):
        if not self.location:
            return None
        region_srid = Region._meta.get_field('geom').srid
        location = self.location.transform(region_srid, clone=True)
        regions = Region.objects.filter(domain=self.domain)
        intersecting = regions.filter(geom__intersects=location)
        return intersecting.first()

    def get_closest_area(self, max_distance=50):
        if not self.location:
            return None
        area_srid = ParkingArea._meta.get_field('geom').srid
        location = self.location.transform(area_srid, clone=True)
        areas = ParkingArea.objects.filter(domain=self.domain)
        with_distance = areas.annotate(distance=Distance('geom', location))
        within_range = with_distance.filter(distance__lte=max_distance)
        closest_area = within_range.order_by('distance').first()
        return closest_area

    def save(self, update_fields=None, *args, **kwargs):
        if not self.domain_id:
            self.domain = EnforcementDomain.get_default_domain()

        if not self.terminal and self.terminal_number:
            self.terminal = ParkingTerminal.objects.filter(
                domain=self.domain,
                number=self.terminal_number).first()

        if self.terminal and not self.location:
            self.location = self.terminal.location

        if update_fields is None or 'region' in update_fields:
            self.region = self.get_region()
        if update_fields is None or 'parking_area' in update_fields:
            self.parking_area = self.get_closest_area()

        if update_fields is None or 'normalized_reg_num' in update_fields:
            self.normalized_reg_num = (
                self.normalize_reg_num(self.registration_number))

        super().save(update_fields=update_fields, *args, **kwargs)

    @classmethod
    def normalize_reg_num(cls, registration_number):
        if not registration_number:
            return ''
        return registration_number.upper().replace('-', '').replace(' ', '')


@with_model_field_modifications(
    created_at={"auto_now_add": False},
    modified_at={"auto_now": False},
    registration_number={"db_index": False},
    time_start={"db_index": False},
    # time_end={"db_index": False},
    normalized_reg_num={"db_index": False},
    domain={"db_index": False},
    location={"db_index": False},
    operator={"db_index": False},
    parking_area={"db_index": False},
    region={"db_index": False},
    terminal={"db_index": False},
    zone={"db_index": False},
)
class ArchivedParking(AbstractParking):
    archived_at = models.DateTimeField(
        auto_now_add=True, db_index=True, verbose_name=_("time archived")
    )
    sanitized_at = models.DateTimeField(verbose_name=_("time sanitized"), null=True, blank=True)

    class Meta:
        verbose_name = _("archived parking")
        verbose_name_plural = _("archived parkings")
        default_related_name = "archived_parkings"

    def __str__(self):
        return super().__str__() + " (archived)"

    def archive(self):
        return self

    @classmethod
    def archive_in_bulk(cls, parkings):
        """
        Archive given parkings in bulk.

        The data from the parkings will be moved to the ArchivedParking
        table with the archived_at value filled with a fresh timestamp.

        :param parkings: QuerySet of Parking objects to archive.
        :returns: A tuple (qs, n) where qs is the queryset of the
                  created ArchivedParking objects and n is the number of
                  deleted Parking objects.
        """
        if issubclass(parkings.model, cls):
            return 0  # Nothing to do, since already archived
        with transaction.atomic():
            archive_copies = cls._create_copies_to_archive(parkings)
            to_delete = parkings.filter(pk__in=archive_copies)
            (deleted_count, _counts_by_type) = to_delete.delete()
        return (archive_copies, deleted_count)

    @classmethod
    def _create_copies_to_archive(cls, parkings):
        """
        Create copies of objects in current queryset to the archive table.

        Generates and executes a SQL query of the form

            INSERT INTO <archive_table> ... SELECT ... FROM <table> ...

        for copying data to the archive table from the current table.

        Effectively this is doing the same as the following Python code,
        but without pulling the data from the DBMS to Python side:

            archived_parkings = [x.make_archived_parking() for x in parkings]
            created = cls.objects.bulk_create(archived_parkings)
            return cls.objects.filter(pk__in=[x.pk for x in created])
        """
        db = router.db_for_write(cls)
        connection = connections[db]
        quote = connection.ops.quote_name
        pk_field = parkings.model._meta.pk
        ids_queryset = parkings.values(pk_field.name)
        (ids_sql, ids_params) = ids_queryset.query.sql_with_params()
        common_columns = [quote(x.column) for x in parkings.model._meta.fields]
        dest_columns = common_columns + [quote("archived_at")]
        src_columns = common_columns + ["%s"]
        copy_values_with_insert_select_sql = (
            "INSERT INTO {dest_table} ({dest_columns})"
            " SELECT {src_columns} FROM {src_table}"
            " WHERE {pk_column} IN ({subquery})"
        ).format(
            dest_table=quote(cls._meta.db_table),
            dest_columns=",".join(dest_columns),
            src_columns=",".join(src_columns),
            src_table=quote(parkings.model._meta.db_table),
            pk_column=quote(pk_field.column),
            subquery=ids_sql,
        )
        archived_at = timezone.now()
        params = (archived_at,) + ids_params
        with connection.cursor() as cursor:
            cursor.execute(copy_values_with_insert_select_sql, params)
        return cls.objects.filter(archived_at=archived_at)

    def sanitize(self):
        self.registration_number = sanitize_registration_number(self.registration_number)
        self.normalized_reg_num = sanitize_registration_number(self.normalized_reg_num)
        self.sanitized_at = timezone.now()
        self.save(update_fields=['registration_number', 'normalized_reg_num', 'sanitized_at'])
