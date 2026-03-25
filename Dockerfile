FROM ubuntu:22.04 AS base

EXPOSE 8000

RUN apt-get update \
    && apt-get install --yes --no-install-recommends \
        gdal-bin \
        python-is-python3 \
        python3 \
        python3-lxml \
        python3-memcache \
        python3-pip \
        python3-psycopg2 \
        python3-wheel

# Set cache path to /tmp/pycache so that pyc files are not read from or
# written to the __pycache__ directories in their normal locations next
# to py files, since those could be used outside of the container and
# may not be compatible with the container's Python.
ENV PYTHONPYCACHEPREFIX=/tmp/pycache

# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED=1

# Disable pip version check to speed up and avoid warnings
ENV PIP_DISABLE_PIP_VERSION_CHECK=1

# Disable pip complaining about being run as root without virtualenv
ENV PIP_ROOT_USER_ACTION=ignore

WORKDIR /app

# Install pip requirements
COPY requirements.txt .
RUN pip install -r requirements.txt

RUN adduser -u 1000 --disabled-password --gecos "" appuser

# ---------------------------------------------------------------------
# Development image

FROM base AS development

RUN apt-get install --no-install-recommends -y \
    build-essential \
    libpq-dev \
    python3-dev \
    pipx

# Install dev, test and style dependencies
COPY requirements-dev.txt .
RUN pip install -r requirements-dev.txt
COPY requirements-test.txt .
RUN pip install -r requirements-test.txt
COPY requirements-style.txt .
RUN pip install -r requirements-style.txt

# Allow appuser to write pyc files to /tmp/pycache
RUN mkdir -p /tmp/pycache && \
    chgrp appuser /tmp/pycache && \
    chmod g+w /tmp/pycache && \
    chown appuser /tmp/pycache

COPY . /app
RUN chown -R appuser /app

ENV DEBUG=1
USER appuser
ENTRYPOINT ["./docker-entrypoint"]

# ---------------------------------------------------------------------
# Production image

FROM base AS production
RUN apt-get install --no-install-recommends -y uwsgi uwsgi-plugin-python3
COPY . /app
RUN python -m compileall .

RUN mkdir /app/var && chown -R appuser /app/var

ENV RUN_MODE=production
ENV DEBUG=0
USER appuser
ENTRYPOINT ["./docker-entrypoint"]
