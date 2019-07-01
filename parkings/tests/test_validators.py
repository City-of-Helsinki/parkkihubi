import pytest

from ..validators import DictListValidator, Field, TextField, TimestampField


def test_dict_list_validator_eq_with_empty_instances():
    assert DictListValidator({}) == DictListValidator({})


def test_dict_list_validator_eq_with_simple_equal_instances():
    a = DictListValidator({
        'foo': TimestampField(),
        'bar': TextField(max_length=100),
    })
    b = DictListValidator({
        'foo': TimestampField(),
        'bar': TextField(max_length=100),
    })

    result = (a == b)

    assert result is True


def test_dict_list_validator_eq_with_unequal_instances_1():
    a = DictListValidator({
        'foo': TimestampField(),
        'bar': TextField(max_length=100),
    })
    b = DictListValidator({
        'foo': TimestampField(),
        'bar': TextField(max_length=100),
        'baz': TimestampField(),
    })

    result = (a == b)

    assert result is False


def test_dict_list_validator_eq_with_unequal_instances_2():
    a = DictListValidator({
        'foo': TimestampField(),
        'bar': TextField(max_length=100),
    })
    b = DictListValidator({
        'foo': TimestampField(),
        'bar': TextField(max_length=123),
    })

    result = (a == b)

    assert result is False


@pytest.mark.parametrize('value', [None, 42, 'foobar', 3.25])
def test_field_clean_value(value):
    field = Field()

    result = field.clean_value(value)

    assert result == value


def test_field_eq_with_equal_instance():
    assert Field() == Field()


@pytest.mark.parametrize('other', [None, 42, 'foobar', TimestampField()])
def test_field_eq_with_unequal_instance(other):
    result = (Field() == other)

    assert result is False
