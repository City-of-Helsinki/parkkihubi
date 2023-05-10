import datetime
import logging
from typing import Optional

from django.conf import ImproperlyConfigured, settings
from django.utils import timezone

from .models import ArchivedParking, Parking, ParkingCheck, Permit
from .utils.querysets import make_batches

LOG = logging.getLogger(__name__)

# A list of queryset methods that return a queryset of ended items.
#
# These methods take a cutoff time (datetime) as an argument and return
# a queryset of items that have ended before that cutoff time.  They
# will be used to scope the anonymization to only items that have ended.
#
# This list also defines which models are anonymized.
#
# The queryset of each model should have an `unanonymized` method that
# returns a queryset of items that have not yet been anonymized, and
# additionally an `anonymize` method that anonymizes the items in the
# queryset.
ENDED_ITEMS_QUERYSET_METHODS = [
    ArchivedParking.objects.ends_before,
    Parking.objects.ends_before,
    ParkingCheck.objects.created_before,
    Permit.objects.all_items_end_before,
]

# Map from model to queryset method.  Used in the implementation.
ENDED_ITEMS_QS_METHODS_BY_MODEL = {
    x.__self__.model: x for x in ENDED_ITEMS_QUERYSET_METHODS
}


def anonymize_all(
    cutoff: Optional[datetime.datetime] = None,
    dry_run: bool = False,
) -> int:
    cutoff = cutoff if cutoff is not None else get_default_cutoff_date()
    LOG.info("Anonymization of items that ended before %s", cutoff)

    total = 0

    for model in ENDED_ITEMS_QS_METHODS_BY_MODEL:
        total += anonymize_model(model, cutoff=cutoff, dry_run=dry_run)

    return total


def anonymize_model(
    model,
    cutoff: Optional[datetime.datetime] = None,
    dry_run: bool = False,
    batch_size: int = 200000,
) -> int:
    cutoff = cutoff if cutoff is not None else get_default_cutoff_date()
    ended_items_qs_method = ENDED_ITEMS_QS_METHODS_BY_MODEL[model]
    ended_items = ended_items_qs_method(cutoff)
    to_anonymize = ended_items.unanonymized()

    count = to_anonymize.count()

    if not count:
        LOG.info("No %s objects to anonymize.", model.__name__)
        return 0

    verb = "Anonymizing" if not dry_run else "(DRY-RUN) Would anonymize"

    LOG.info("%s %d %s objects...", verb, count, model.__name__)

    if dry_run:
        return 0

    total_anonymized = 0

    for batch in make_batches(to_anonymize, batch_size, "created_at"):
        anonymized = batch.anonymize()
        total_anonymized += anonymized
        items_left = count - total_anonymized
        if items_left > 0:
            LOG.info("...still %d objects to anonymize...", items_left)

    if total_anonymized != count:
        LOG.warning((
            "Anonymization returned %d as number of anonymized objects, "
            "but excpeted %d"), total_anonymized, count)

    return total_anonymized


def get_default_cutoff_date():
    limit = settings.PARKKIHUBI_REGISTRATION_NUMBERS_REMOVABLE_AFTER
    if not isinstance(limit, datetime.timedelta):
        raise ImproperlyConfigured(
            "PARKKIHUBI_REGISTRATION_NUMBERS_REMOVABLE_AFTER must be "
            "a timedelta"
        )
    return timezone.now() - limit
