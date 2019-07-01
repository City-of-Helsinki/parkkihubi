from django.contrib.postgres.fields import JSONField


class CleaningJsonField(JSONField):
    """
    JSON Field that cleans its values with the validators.
    """
    def to_python(self, value):
        value = super().to_python(value)
        for validator in self.validators:
            if callable(getattr(validator, 'clean', None)):
                value = validator.clean(value)
        return value
