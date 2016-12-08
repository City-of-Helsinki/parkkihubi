from django.conf.urls import include, url
from django.contrib import admin

from parkings.api.internal import urls as internal_urls
from parkings.api.operator import urls as operator_urls

urlpatterns = [
    url(r'^internal/v1/', include(internal_urls)),
    url(r'^operator/v1/', include(operator_urls)),
    url(r'^admin/', admin.site.urls),
]
