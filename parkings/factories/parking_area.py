import factory
from django.contrib.gis.geos import MultiPolygon, Point, Polygon
from django.utils.crypto import get_random_string

from parkings.models import ParkingArea

from .faker import fake


def generate_point():
    return Point(
        24.915 + fake.random.uniform(0, 0.040),
        60.154 + fake.random.uniform(0, 0.022),
        srid=4326,
    )


def generate_polygon():
    center = generate_point()
    points = [
        Point(
            center.x + fake.random.uniform(-0.001, 0.001),
            center.y + fake.random.uniform(-0.001, 0.001),
            srid=4326,
        ).transform(3879, clone=True)
        for _ in range(3)
    ]
    points.append(points[0])
    return Polygon(points)


def generate_multi_polygon():
    return MultiPolygon(generate_polygon())


def generate_origin_id():
    return get_random_string(32)


class ParkingAreaFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ParkingArea

    geom = factory.LazyFunction(generate_multi_polygon)
    capacity_estimate = fake.random.randint(1, 50)
    origin_id = factory.LazyFunction(generate_origin_id)
