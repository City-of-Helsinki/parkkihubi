import abc
import json

from django.contrib.gis.geos import GEOSGeometry, MultiPolygon, Polygon


class GeoJsonImporter(metaclass=abc.ABCMeta):

    def read_and_parse(self, geojson_file_path):
        with open(geojson_file_path, "rt") as file:
            root = json.load(file)
            for member in root['features']:
                yield self._parse_member(member)

    @abc.abstractmethod
    def _parse_member(self, member):
        pass

    def get_polygons(self, geom):
        result = GEOSGeometry(json.dumps(geom))

        if isinstance(result, Polygon):
            result = MultiPolygon(result)

        return result
