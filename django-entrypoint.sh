#!/bin/bash

set -e

if ["$1" != "production" -o "$1" != "development"]; then
    "$@"
    exit $?
fi


until nc -z -v -w30 "db" 5432
do
    echo "Waiting for database connection..."
    sleep 1
done

echo "Apply database migrations"
./manage.py migrate --noinput


if ["$1" == "production"]; then
    echo "Running production server"
    # TODO: Run server in production
else
    echo "Running development server"
    exec ./manage.py runserver 0.0.0.0:8000
fi
