#!/usr/bin/env python
"""
Fix invalid geometries of a model in the database.

Some of the (imported) geometries might be invalid.  This causes
problems, because it makes many GIS database queries fail .  This
command can be used to fix those geometries.

Currently supports only MultiPolygon geometries.
"""
import re
import sys

from django.apps import apps as django_apps
from django.contrib.gis.db.models.fields import MultiPolygonField
from django.contrib.gis.db.models.functions import MakeValid
from django.contrib.gis.geos import GeometryCollection, MultiPolygon, Polygon
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = __doc__.strip().splitlines()[0]

    def add_arguments(self, parser):
        parser.add_argument(
            'model_name', type=str,
            help=("Name of the model to fix, e.g. \"ParkingArea\""))

        parser.add_argument(
            '--dry-run', '-n', action='store_true',
            help=("Dry run, i.e. just show what would be fixed"))

    def handle(self, model_name, dry_run=False, *args, **options):
        verbosity = int(options['verbosity'])
        show_info = self.stdout.write if verbosity >= 1 else (lambda x: None)
        show_debug = self.stdout.write if verbosity >= 2 else (lambda x: None)

        model_full_name = ('parkings.' + model_name
                           if '.' not in model_name else model_name)
        model = django_apps.get_model(model_full_name)
        geometry_fields = [
            field for field in model._meta.get_fields()
            if isinstance(field, MultiPolygonField)]

        if len(geometry_fields) != 1:
            sys.exit("Model should have exactly one MultiPolygon field")

        field_name = geometry_fields[0].name

        objects_to_fix = (
            model.objects.order_by('pk')
            .filter(**{field_name + '__isvalid': False})
            .annotate(**{'valid_geom': MakeValid(field_name)}))

        if not objects_to_fix:
            show_info("All good. Nothing to fix.")
            return

        for obj in objects_to_fix:
            obj_info = '{field_name} of {model_name}:{obj.pk} / {obj}'.format(
                field_name=field_name, model_name=model_name, obj=obj)
            show_info("Doing {}".format(obj_info))
            show_debug("  original geometry: {}".format(
                _geom_info(getattr(obj, field_name), verbosity)))
            show_debug("  after MakeValid:   {}".format(
                _geom_info(obj.valid_geom, verbosity)))
            fixed_geom = _to_multipolygon(obj.valid_geom)
            show_debug("  after conversion:  {}".format(
                _geom_info(fixed_geom, verbosity)))
            if dry_run:
                show_info("  Not saved, since doing dry-run.")
            else:
                setattr(obj, field_name, fixed_geom)
                obj.save()
                show_info("  Fixed.")


def _polygon_to_multipolygon(polygon):
    assert isinstance(polygon, Polygon)
    return MultiPolygon(polygon, srid=polygon.srid)


def _geometry_collection_to_multipolygon(geometry_collection):
    assert isinstance(geometry_collection, GeometryCollection)
    return _get_multipolygon_from_collection(geometry_collection)


def _multipolygon_to_multipolygon(multipolygon):
    assert isinstance(multipolygon, MultiPolygon)
    return _get_multipolygon_from_collection(multipolygon)


def _get_multipolygon_from_collection(geometry_collection):
    polygons = []
    for geom in geometry_collection:
        if geom.dims < 2:
            # Just ignore everything that has dimension 0 or 1,
            # i.e. points, lines, or linestrings, multipoints, etc.
            continue
        polygons.extend(_to_multipolygon(geom))
    return MultiPolygon(polygons, srid=geometry_collection.srid)


def _to_multipolygon(geometry):
    converter = _geometry_converters[type(geometry)]
    multipolygon = converter(geometry)
    assert isinstance(multipolygon, MultiPolygon)
    assert geometry.srid == multipolygon.srid
    return multipolygon


_geometry_converters = {
    MultiPolygon: _multipolygon_to_multipolygon,
    Polygon: _polygon_to_multipolygon,
    GeometryCollection: _geometry_collection_to_multipolygon,
}


def _geom_info(geometry, verbosity=2):
    text = str(geometry)
    return text if verbosity >= 3 else re.sub(r'\(\d[\d., ]*\)', '(...)', text)
