FROM ubuntu:jammy-20231004

EXPOSE 8000

RUN apt-get update \
    && apt-get install --yes --no-install-recommends \
        gdal-bin \
        python3 \
        python3-cryptography \
        python3-lxml \
        python3-memcache \
        python3-ndg-httpsclient \
        python3-paste \
        python3-pil \
        python3-pip \
        python3-psycopg2 \
        python3-pyasn1 \
        python3-pyproj \
        python3-rcssmin \
        python3-requests \
        python3-six \
        python3-socks \
        python3-urllib3 \
        python3-venv \
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

# Upgrade pip (sending the warning about running as root to /dev/null)
RUN pip install -U pip 2>/dev/null

# Install pip requirements
COPY requirements.txt .
RUN pip install -r requirements.txt

WORKDIR /app

RUN adduser -u 1000 --disabled-password --gecos "" appuser

ENTRYPOINT ["./docker-entrypoint"]

# ---------------------------------------------------------------------
# Development image

FROM base AS development

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

# ---------------------------------------------------------------------
# Production image

FROM base AS production
RUN pip install uwsgi==2.0.21
COPY . /app
RUN python -m compileall .

ENV RUN_MODE=production
ENV DEBUG=0
USER appuser
