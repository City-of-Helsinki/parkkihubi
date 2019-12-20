import sys

from django.contrib.gis.gdal import DataSource
from django.contrib.gis.utils import LayerMapping

from parkings.models import Region


class ShapeFileToRegionImporter(object):
    """
    Importer from ESRI Shapefiles to Region model in the database.
    """
    field_mapping = {
        # Region model field -> Field in the file
        'geom': 'MULTIPOLYGON',
    }

    def __init__(self, filename, encoding='utf-8',
                 output_stream=sys.stderr, verbose=True):
        self.filename = filename
        self.encoding = encoding
        self.data_source = DataSource(filename, encoding=encoding)
        self.output_stream = output_stream
        self.verbose = verbose

    def set_field_mapping(self, mapping):
        self.field_mapping = dict(self.field_mapping, **mapping)

    def get_layer_names(self):
        return [layer.name for layer in self.data_source]

    def get_layer_fields(self, name):
        layer = self.data_source[self._get_layer_index(name)]
        return layer.fields

    def import_from_layer(self, layer_name):
        layer_mapping = LayerMapping(
            model=Region,
            data=self.filename,
            mapping=self.field_mapping,
            layer=self._get_layer_index(layer_name),
            encoding=self.encoding)
        silent = (self.output_stream is None)
        layer_mapping.save(
            strict=True,
            stream=self.output_stream,
            silent=silent,
            verbose=(not silent and self.verbose))

    def _get_layer_index(self, name):
        layer_names = self.get_layer_names()
        try:
            return layer_names.index(name)
        except ValueError:
            raise ValueError('No such layer: {!r}'.format(name))
