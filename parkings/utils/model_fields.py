def with_model_field_modifications(**field_modifications):
    """
    Class decorator to modify model field options.

    This makes it possible to do changes to certain options in the base
    model fields in inherited model without overriding the whole field.
    """

    def modify_model_fields(cls):
        for (field_name, modifications) in field_modifications.items():
            field = cls._meta.get_field(field_name)
            for (option, value) in modifications.items():
                setattr(field, option, value)
        return cls

    return modify_model_fields
