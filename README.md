# Parkkihubi

Parkkihubi is a Django based REST API for processing parking data.

## Requirements

* Python >= 3.10
* PostgreSQL 14 + PostGIS 3.4

Preferred versions are Python 3.12, PostgreSQL 16.13 and PostGIS 3.5 on
Ubuntu 24.04.

Current uv.lock pins Django to 5.2, but 4.2 and 6.0 should also work.

### Python requirements

Use [uv](https://docs.astral.sh/uv/) to install and maintain installed
dependencies.  You may also need build essentials and some development
libraries installed.

    sudo apt-get install build-essential libpq-dev
    pipx install uv  # Or see uv's docs for other install methods

And then, to install the dependencies:

    uv sync

### Django configuration

Environment variables are used to customize base configuration in
`parkkihubi/settings.py`. If you wish to override any settings, you can place
them in a local `.env` file which will automatically be sourced when Django imports
the settings file.

Create a basic file for development as follows

    echo 'DEBUG=True' > .env

#### Parkkihubi settings

- `PARKKIHUBI_PUBLIC_API_ENABLED` default `True`
- `PARKKIHUBI_MONITORING_API_ENABLED` default `True`
- `PARKKIHUBI_OPERATOR_API_ENABLED` default `True`
- `PARKKIHUBI_ENFORCEMENT_API_ENABLED` default `True`

### Running tests

Run all tests

    pytest

Run with coverage

    pytest --cov-report html --cov .

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

With VSCode environment, you can start development server from debug side-bar. You
also need to run migrations and generate static files.

    python manage.py migrate
    python manage.py collectstatic --noinput

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
