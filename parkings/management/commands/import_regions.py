#!/usr/bin/env python
r"""
Import regions from file.

Instructions to import data
===========================

From geoserver.hel.fi
---------------------

 1. Download feature data from http://geoserver.hel.fi/geoserver/web/

    - Click "Layer Preview"
    - Select "Helsinki_osa_alueet"
    - Download as WFS / Shapefile

 2. Unzip the file::

      Helsinki_osa_alueet.zip

 3. Run this import command to the Shapefile::

      ./manage.py import_regions \
           --verbosity 2 \
           --encoding latin1 --name nimi_fi \
           Helsinki_osa_alueet.shp Helsinki_osa_alueet

From ptp.hel.fi/avoindata
-------------------------

 1. Download feature data from http://ptp.hel.fi/avoindata/ link
    "Helsingin piirialuejako vuosilta 1995-2016 (zip) 24.2.2017
    Paikkatietohakemisto GeoPackage (ETRS-GK25 (EPSG:3879))", or use
    direct link:

    http://ptp.hel.fi/avoindata/aineistot/HKI-aluejako-1995-2016-gpkg.zip

 2. Unzip the file

 3. Install tools for Geographic data conversion::

      sudo apt install gdal-bin  # Works on Ubuntu

 4. Convert the GeoPackage data to ESRI Shapefile format::

      ogr2ogr piirialuejako.shp piirialuejako-1995-2016.gpkg

 5. Run this import command to the converted shp file::

      ./manage.py import_regions piirialuejako.shp osa_alue_2016
"""
import argparse

from django.core.management.base import BaseCommand

from ...importers.regions import ShapeFileToRegionImporter


class Command(BaseCommand):
    help = __doc__.strip().splitlines()[0]

    def create_parser(self, prog_name, subcommand):
        parser = super().create_parser(prog_name, subcommand)
        parser.epilog = '\n'.join(__doc__.strip().splitlines()[2:])
        parser.formatter_class = argparse.RawDescriptionHelpFormatter
        return parser

    def add_arguments(self, parser):
        parser.add_argument(
            'filename', type=str,
            help=("Path to the ESRI Shapefile (*.shp) to import from"))

        parser.add_argument(
            'layer_name', type=str,
            help=("Name of the layer to import or \"LIST\" to get a list"))

        parser.add_argument('--encoding', type=str, default='utf-8')
        parser.add_argument('--name-field', type=str, default='Nimi')

    def handle(self, filename, layer_name, encoding, name_field,
               *args, **options):
        verbosity = int(options['verbosity'])
        importer = ShapeFileToRegionImporter(
            filename,
            encoding=encoding,
            output_stream=(self.stdout if verbosity > 0 else None),
            verbose=(verbosity >= 2))

        importer.set_field_mapping({'name': name_field})

        if layer_name == 'LIST':
            for name in importer.get_layer_names():
                self.stdout.write(name)
                for field in importer.get_layer_fields(name):
                    self.stdout.write(' - {}'.format(field))
        else:
            importer.import_from_layer(layer_name)
