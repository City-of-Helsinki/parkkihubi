FROM python:3.7-slim-buster AS base

EXPOSE 8000

# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE=1

# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED=1

# Install system dependencies
RUN apt-get update  \
    && \
    apt-get install --no-install-recommends -y \
      gdal-bin \
      python3-gdal \
      netcat \
      libpq-dev \
      build-essential

# Install pip requirements
COPY requirements.txt .
RUN python -m pip install -r requirements.txt

WORKDIR /app

RUN adduser -u 5678 --disabled-password --gecos "" appuser

ENTRYPOINT ["./docker-entrypoint"]

# ---------------------------------------------------------------------
# Development image

FROM base AS development
COPY requirements-dev.txt .
RUN pip install -r requirements-dev.txt
COPY requirements-test.txt .
RUN pip install -r requirements-test.txt
COPY requirements-style.txt .
RUN pip install -r requirements-style.txt
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
