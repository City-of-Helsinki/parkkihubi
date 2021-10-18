[![Build status](https://travis-ci.org/City-of-Helsinki/parkkihubi.svg?branch=master)](https://travis-ci.org/City-of-Helsinki/parkkihubi)
[![codecov](https://codecov.io/gh/City-of-Helsinki/parkkihubi/branch/master/graph/badge.svg)](https://codecov.io/gh/City-of-Helsinki/parkkihubi)
[![Requirements](https://requires.io/github/City-of-Helsinki/parkkihubi/requirements.svg?branch=master)](https://requires.io/github/City-of-Helsinki/parkkihubi/requirements/?branch=master)

# Parking hub

Django-based REST API for processing parking data.

## Requirements

* Python 3.x
* PostgreSQL + PostGIS

## Development

### Install required system packages

#### PostgreSQL

The recommended versions for postgresql and postgis are at least 9.4 and 2.2 respectively.

    # Ubuntu 16.04
    sudo apt-get install python3-dev libpq-dev postgresql postgis

#### GeoDjango extra packages

    # Ubuntu 16.04
    sudo apt-get install binutils libproj-dev gdal-bin

### Creating a virtualenv

Create a Python 3.x virtualenv either using the traditional `virtualenv` tool or using the great `virtualenvwrapper` toolset. Assuming the former, [once installed](https://virtualenvwrapper.readthedocs.io/en/latest/), simply do:

    mkvirtualenv -p /usr/bin/python3 parkkihubi

The virtualenv will automatically activate. To activate it in the future, just do:

    workon parkkihubi

### Python requirements

Use `pip-tools` to install and maintain installed dependencies.

    pip install -U pip  # pip-tools needs pip==6.1 or higher (!)
    pip install pip-tools

Install requirements as follows

    pip-sync requirements.txt requirements-dev.txt

### Django configuration

Environment variables are used to customize configuration in `parkkihubi/settings.py`. If you wish to override any settings, you can place them in a local `.env` file which will automatically be sourced when Django imports the settings file.

Create a basic file for development as follows

    echo 'DEBUG=True' > .env

#### Parkkihubi settings

- `PARKKIHUBI_PUBLIC_API_ENABLED` default `True`
- `PARKKIHUBI_MONITORING_API_ENABLED` default `True`
- `PARKKIHUBI_OPERATOR_API_ENABLED` default `True`
- `PARKKIHUBI_ENFORCEMENT_API_ENABLED` default `True`

### Database

Create user and database

    sudo -u postgres createuser -P -R -S parkkihubi  # use password `parkkihubi`
    sudo -u postgres createdb -O parkkihubi parkkihubi
    sudo -u postgres psql parkkihubi -c "CREATE EXTENSION postgis;"

Allow user to create test database

    sudo -u postgres psql -c "ALTER USER parkkihubi CREATEDB;"

Tests also require that PostGIS extension is installed on the test database. This can be achieved most easily by adding PostGIS extension to the default template:

    sudo -u postgres psql -d template1 -c "CREATE EXTENSION IF NOT EXISTS postgis;"

Run migrations

    python manage.py migrate

### Updating requirements files

Use Prequ to update the `requirements*.txt` files.

    pip install prequ

When you change requirements, set them in `requirements.in` or `requirements-dev.in`. Then run:

    prequ update

### Running tests

Run all tests

    py.test

Run with coverage

    py.test --cov-report html --cov .

Open `htmlcov/index.html` for the coverage report.

### Importing parking areas

To import Helsinki parking areas run:

    python manage.py import_parking_areas

### Geojson importers

To import payment zones from geojson run:

    python manage.py import_geojson_payment_zones --domain=HKI  <GEOJSON_FILE_PATH>

To import permit areas from geojson run:

    python manage.py import_geojson_permit_areas --domain=HKI <GEOJSON_FILE_PATH>

### Starting a development server

    python manage.py runserver

Operator API will be available at [http://127.0.0.1:8000/operator/v1/](http://127.0.0.1:8000/operator/v1/)

Enforcement API will be available at
http://127.0.0.1:8000/enforcement/v1/

Public API will be available at [http://127.0.0.1:8000/public/v1/](http://127.0.0.1:8000/public/v1/)

### Generating API documentation

The API documentation conforms to [Swagger Specification 2.0](http://swagger.io/specification/).

Three possible ways (out of many) to generate the documentation:

- Run the documentation generating script:

      ./generate-docs

  The output will be in `docs/generated` directory by default.  If you
  want to generate to a different directory, give that directory as the
  first argument to the script.

- [bootprint-openapi](https://github.com/bootprint/bootprint-openapi)

    Probably the recommended way.

    Installation:

      npm install -g bootprint
      npm install -g bootprint-openapi

    Running (in `parkkihubi` repository root):

      bootprint openapi docs/api/enforcement.yaml </output/path/enforcement/>
      bootprint openapi docs/api/operator.yaml </output/path/operator/>

- [swagger-codegen](https://github.com/swagger-api/swagger-codegen)

    Due to [a bug in swagger-codegen](https://github.com/swagger-api/swagger-codegen/pull/4508),
    we're using an unreleased version at the moment.
    
    To build swagger-codegen from source, you need Apache maven installed (you'll
    need java 7 runtime at a minimum):
    
        # Ubuntu
        sudo apt-get install maven
    
    Clone swagger-codegen master branch and build it:
    
        git clone https://github.com/swagger-api/swagger-codegen
        cd swagger-codegen/
        mvn clean package  # Takes a few minutes
    
    The client will now be available at `modules/swagger-codegen-cli/target/swagger-codegen-cli.jar`.
    
    To build the docs, in `parkkihubi` repository root:
    
        cd docs/api
        java -jar /path/to/codegen/swagger-codegen-cli.jar generate \
          -i enforcement.yaml -l html2 -c config.json \
          -o /output/path/enforcement/
        java -jar /path/to/codegen/swagger-codegen-cli.jar generate \
          -i operator.yaml -l html2 -c config.json \
          -o /output/path/operator/

## License

[MIT](https://tldrlegal.com/license/mit-license)
