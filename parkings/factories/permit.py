import factory

from parkings.models import Permit, PermitSeries


def generate_areas(count=3):
    from parkings.tests.utils import generate_areas
    return generate_areas(count)


def generate_external_ids():
    from parkings.tests.utils import generate_external_ids
    return generate_external_ids()


def generate_subjects(count=2):
    from parkings.tests.utils import generate_subjects
    return generate_subjects()


class PermitSeriesFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = PermitSeries


class PermitFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Permit

    series = factory.SubFactory(PermitSeriesFactory)
    external_id = factory.LazyFunction(lambda: generate_external_ids())
    subjects = factory.LazyFunction(lambda: generate_subjects(count=2))
    areas = factory.LazyFunction(lambda: generate_areas(count=3))


class ActivePermitFactory(PermitFactory):
    series = factory.LazyFunction(lambda: PermitSeriesFactory(active=True))
