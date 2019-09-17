from datetime import timezone

from dateutil.parser import parse as parse_datetime
from django.core.exceptions import ValidationError
from django.utils.deconstruct import deconstructible
from django.utils.translation import gettext as _


class Field:
    def clean_value(self, value):
        return value

    def __eq__(self, other):
        return (type(self) == type(other))


@deconstructible
class TextField(Field):
    def __init__(self, *, max_length):
        assert isinstance(max_length, int)
        self.max_length = max_length

    def clean_value(self, value):
        if not isinstance(value, str):
            raise ValidationError(_('Not a string'))

        if len(value) > self.max_length:
            raise ValidationError(_(
                'Value longer than {} characters'.format(self.max_length)))

        return value

    def __eq__(self, other):
        return (type(self) == type(other) and
                self.max_length == other.max_length)


@deconstructible
class TimestampField(TextField):
    def __init__(self, *, max_length=None):
        super().__init__(max_length=(max_length or 100))

    def clean_value(self, value):
        value = super().clean_value(value)

        try:
            dt = parse_datetime(value)
        except ValueError:
            raise ValidationError(_('Not a timestamp string'))

        if not dt.tzinfo:
            raise ValidationError(_('Missing timezone'))

        return dt.astimezone(timezone.utc).isoformat()


@deconstructible
class DictListValidator:
    def __init__(self, item_schema):
        assert isinstance(item_schema, dict)
        assert all(isinstance(x, str) for x in item_schema.keys())
        assert all(isinstance(x, Field) for x in item_schema.values())
        self.item_schema = item_schema

    def __call__(self, value):
        self.clean(value)

    def clean(self, value):
        if not isinstance(value, list):
            raise ValidationError(_('Must be a list'), code='invalid-type')
        return [self._clean_item(x) for x in value]

    def _clean_item(self, item):
        if not isinstance(item, dict):
            raise ValidationError(
                _('Each list item must be a dictionary'),
                code='invalid-item-type')

        extra_fields = set(item.keys()) - set(self.item_schema.keys())

        if extra_fields:
            raise ValidationError(
                _('Unknown fields in item: {}').format(
                    ', '.join(sorted(extra_fields))),
                code='unknown-item-fields')

        return dict(self._clean_item_fields(item))

    def _clean_item_fields(self, item):
        for field in self.item_schema.keys():
            try:
                value = item[field]
            except KeyError:
                raise ValidationError(
                    _('Field "{}" is missing from an item').format(field),
                    code='missing-item-field')
            else:
                yield (field, self._clean_item_field(field, value))

    def _clean_item_field(self, field, value):
        expected_type = self.item_schema[field]  # type: Field
        try:
            return expected_type.clean_value(value)
        except ValidationError as error:
            raise ValidationError(
                _('Invalid "{field}" value {value!r}: {error}').format(
                    field=field, value=value, error=error.messages[0]),
                code='invalid-item-field-type')

    def __eq__(self, other):
        return (
            type(self) == type(other) and
            self.item_schema == other.item_schema)
