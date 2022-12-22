from django.db.models import Q


def make_batches(queryset, batch_size, order_by_field):
    if queryset.filter(**{order_by_field: None}).exists():
        raise ValueError(
            "Found NULL values in order-by field ({f}) for {qs}".format(
                f=order_by_field, qs=queryset.values("pk").query
            )
        )

    ordered_qs = queryset.order_by(order_by_field, "pk")
    window = ordered_qs
    found_last_batch = False
    while not found_last_batch:
        last_item_slice = window[(batch_size - 1):batch_size]
        last = last_item_slice.values("pk", order_by_field).first()
        if not last:  # If there was less than batch_size items left
            last = window.values("pk", order_by_field).last()
            found_last_batch = True
            if not last:
                break
        (cut_value, cut_pk) = (last[order_by_field], last["pk"])
        items_before_q = _items_before(cut_value, cut_pk, order_by_field)
        batch = window.filter(items_before_q)
        yield batch
        window = ordered_qs.exclude(items_before_q)


def _items_before(cut_value, cut_pk, field_name):
    """
    Generate a Q term for filtering values before certain cut point.

    The cut point is a pair of cut_value and cut_pk so that the result
    will be in effect a Q item with following conditions:

        X < cut_value OR (X = cut_value AND pk <= cut_pk)

    where X is the value of the field with given field_name.

    We also add an optimization term X <= cut_value which is ANDed with
    the previous conditions.  That doesn't make a difference to the
    filtering, but improves the performance, because it seems that
    PostgreSQL is smarter in its index usage with that term.
    """
    # Note: q0 term doesn't affect result, but improves query performance
    q0 = Q(**{field_name + "__lte": cut_value})  # field value <= cut_value
    q1 = Q(**{field_name + "__lt": cut_value})  # field value < cut_value
    q2 = Q(**{
        field_name: cut_value,  # field value = cut_value
        "pk__lte": cut_pk,  # pk <= cut_pk
    })
    return q0 & (q1 | q2)
