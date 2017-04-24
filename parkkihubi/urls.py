from django.conf.urls import include, url
from django.contrib import admin

from parkings.api.internal import urls as internal_urls
from parkings.api.operator import urls as operator_urls
from parkings.api.public import urls as public_urls

urlpatterns = [
    url(r'^internal/v1/', include(internal_urls, namespace='internal')),
    url(r'^operator/v1/', include(operator_urls, namespace='operator')),
    url(r'^public/v1/', include(public_urls, namespace='public')),
    url(r'^admin/', admin.site.urls),
]
