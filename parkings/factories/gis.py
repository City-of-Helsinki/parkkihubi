from django.contrib.gis.geos import MultiPolygon, Point, Polygon

from .faker import fake


def generate_location(
    lat_min=60.154,
    lat_max=60.176,
    long_min=24.915,
    long_max=24.955,
    srid=4326,
):
    return Point(
        long_min + fake.random.uniform(0, long_max - long_min),
        lat_min + fake.random.uniform(0, lat_max - lat_min),
        srid=srid,
    )


def generate_polygon():
    center = generate_location()
    # Create a square area that covers the generated locations for sure
    wgs84_points = [
        Point(center.x - 0.040, center.y - 0.022, srid=4326),
        Point(center.x + 0.040, center.y - 0.022, srid=4326),
        Point(center.x + 0.040, center.y + 0.022, srid=4326),
        Point(center.x - 0.040, center.y + 0.022, srid=4326),
    ]
    points = [p.transform(3879, clone=True) for p in wgs84_points]
    points.append(points[0])
    return Polygon(points)


def generate_multi_polygon():
    return MultiPolygon(generate_polygon())
