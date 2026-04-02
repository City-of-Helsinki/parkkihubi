from django.urls import include, re_path


def versioned_url(version, include_urls, regexp=r'^'):
    return re_path(
        '{regexp}{version}/'.format(regexp=regexp, version=version),
        include((include_urls, version)))
