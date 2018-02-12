import pytest
from django.contrib.gis.geos import MultiPolygon, Polygon

from parkings.models import ParkingArea, Region


def test_str():
    assert str(Region(name='Foobba')) == 'Foobba'
    assert str(Region(name=None)) == 'Unnamed region'
    assert str(Region(name='')) == 'Unnamed region'
    assert isinstance(str(Region()), str)


@pytest.mark.django_db
def test_calculate_capacity_estimate():
    """
    Test Region capacity estimate calculation.

    Construct the following geometries:

      - reg = Region to estimate
      - pa1 = Parking area 1, capacity=3, inside reg
      - pa2 = Parking area 2, capacity=4, inside reg
      - pa3 = Parking area 3, capacity=15, 1/3 of area inside reg
      - pa4 = Parking area 4, capacity=20, outside reg

    Total capacity should be 3 + 4 + (1/3)*15 = 12.

    Same as a graph::

        +-------------------------------+
        |       reg                     |
        | +--------+  +---------+ +---------------------+ +-------...
        | |  pa1   |  |   pa2   | |     |   pa3         | |  pa4
        | +--------+  +---------+ +---------------------+ +-------...
        | capacity=3  capacity=4        | capacity=15     capacity=20
        |                               |
        +-------------------------------+
    """
    def rect(topleft, width, height):
        """
        Construct a rectangle as multipolygon.
        """
        (ax, ay) = topleft  # left = ax, top = ay
        (bx, by) = (ax + width, ay + height)  # right = bx, bottom = by
        return MultiPolygon(Polygon(
            [(ax, ay), (ax, by), (bx, by), (bx, ay), (ax, ay)]))

    reg = Region(geom=rect((0, 0), 100, 14))
    pa1 = ParkingArea(geom=rect((2, 2), 20, 10), capacity_estimate=3)
    pa2 = ParkingArea(geom=rect((30, 2), 20, 10), capacity_estimate=4)
    pa3 = ParkingArea(geom=rect((60, 2), 120, 10), capacity_estimate=15)
    pa4 = ParkingArea(geom=rect((200, 2), 40, 10), capacity_estimate=20)

    assert reg.geom.area == 1400
    assert pa1.geom.area == 200
    assert pa2.geom.area == 200
    assert pa3.geom.area == 1200
    assert pa4.geom.area == 400

    assert reg.geom.intersection(pa1.geom).area == pa1.geom.area
    assert reg.geom.intersection(pa2.geom).area == pa2.geom.area
    assert reg.geom.intersection(pa3.geom).area == pa3.geom.area / 3
    assert reg.geom.intersection(pa4.geom).area == 0

    # Save them to the database
    reg.save()
    for (n, pa) in enumerate([pa1, pa2, pa3, pa4]):
        pa.origin_id = 'PA-{}'.format(n)
        pa.save()

    # And finally, check the result of the calculation is correct
    assert reg.calculate_capacity_estimate() == 12
