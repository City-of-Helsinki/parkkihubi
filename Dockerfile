FROM python:3.7-slim as appbase

ENV PYTHONBUFFERED 1

RUN apt-get update  \
    && \
    apt-get install --no-install-recommends -y \
      gdal-bin \
      python3-gdal \
      netcat \
      libpq-dev \
      build-essential

WORKDIR /app

COPY requirements.txt ./requirements.txt

RUN pip install --no-cache-dir -r requirements.txt \
    && \
    apt-get remove -y build-essential libpq-dev \
    && \
    apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false \
    && \
    rm -rf /var/lib/apt/lists/* \
    && \
    rm -rf /var/cache/apt/archives


COPY . .

ENTRYPOINT ["/app/django-entrypoint.sh"]

# TODO: Production environment
# Production environment
# CMD ["production"]


# Development environment
FROM appbase as development

COPY requirements-*.txt ./

RUN pip install --no-cache-dir \
    -r requirements-dev.txt \
    -r requirements-style.txt \
    -r requirements-test.txt

CMD ["development"]
