from django.conf.urls import include, url


def versioned_url(version, include_urls, regexp=r'^'):
    return url(
        '{regexp}{version}/'.format(regexp=regexp, version=version),
        include((include_urls, version)))
