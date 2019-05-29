from django.contrib.gis.geos import MultiPolygon, Point, Polygon


def get_polygons(geom):
        """
        Turns the XML containing coordinates into a multipolygon
        """
        polygons = []

        for pos in geom.iter('*'):
            # get leaf nodes. Treat LinearRing and MultiSurface the same way
            if len(pos) == 0:
                positions = list(filter(None, pos.text.split(' ')))
                points = []
                points_as_pairs = zip(positions[1::2], positions[::2])
                for latitude, longitude in points_as_pairs:
                    points.append(Point(float(latitude), float(longitude)))
                polygons.append(Polygon(points))

        return MultiPolygon(polygons)
