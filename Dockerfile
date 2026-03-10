FROM ubuntu:22.04 AS base

EXPOSE 8000

RUN --mount=type=cache,sharing=locked,target=/var/lib/apt/lists \
    --mount=type=cache,sharing=locked,target=/var/cache/apt \
    rm -f /etc/apt/apt.conf.d/docker-clean && \
    apt-get update && \
    DEBIAN_FRONTEND=noninteractive \
    apt-get install -y --no-install-recommends \
    python-is-python3 \
    python3 \
    python3-dev \
    python3-pip \
    python3-wheel \
    gettext \
    postgresql-client \
    libpq-dev \
    libpcre2-dev \
    libgdal-dev \
    tzdata \
    build-essential

RUN pip install uv

RUN adduser -u 1000 --disabled-password --gecos "" appuser

WORKDIR /app

USER appuser

ENV VIRTUALENV=/home/appuser/venv
ENV UV_PROJECT_ENVIRONMENT=$VIRTUALENV
ENV PATH=$VIRTUALENV/bin:/usr/local/bin:/usr/bin:/bin

# Set Python cache path so that pyc files are not read from or
# written to the __pycache__ directories in their normal locations next
# to py files, since those could be used outside of the container and
# may not be compatible with the container's Python.
RUN mkdir -p /home/appuser/.cache/pycache
ENV PYTHONPYCACHEPREFIX=/home/appuser/.cache/pycache

# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED=1

# Set VAR_ROOT under home dir to ensure it's writable
RUN mkdir /home/appuser/var
ENV VAR_ROOT=/home/appuser/var

# Install dependencies
COPY pyproject.toml uv.lock .

RUN --mount=type=cache,sharing=locked,uid=1000,target=/home/appuser/.cache/uv \
    uv sync --locked --no-default-groups

# ---------------------------------------------------------------------
# Development image

FROM base AS development

# Install dev, test and style dependencies
RUN --mount=type=cache,sharing=locked,uid=1000,target=/home/appuser/.cache/uv \
    uv sync --locked --all-groups

COPY . /app

ENV DEBUG=1

ENTRYPOINT ["./docker-entrypoint"]

# ---------------------------------------------------------------------
# Production image

FROM base AS production

USER root
RUN --mount=type=cache,sharing=locked,target=/var/lib/apt/lists \
    --mount=type=cache,sharing=locked,target=/var/cache/apt \
    rm -f /etc/apt/apt.conf.d/docker-clean && \
    apt-get update && \
    apt-get install --no-install-recommends -y uwsgi uwsgi-plugin-python3
USER appuser

COPY . /app
RUN python -m compileall .

ENV RUN_MODE=production
ENV DEBUG=0

ENTRYPOINT ["./docker-entrypoint"]
