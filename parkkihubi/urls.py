from django.conf import settings
from django.conf.urls import include, url
from django.contrib import admin

from parkings.api.auth import urls as auth_urls
from parkings.api.enforcement import urls as enforcement_urls
from parkings.api.monitoring import urls as monitoring_urls
from parkings.api.operator import urls as operator_urls
from parkings.api.public import urls as public_urls

urlpatterns = [
    url(r'^auth/', include(auth_urls)),
]

if getattr(settings, 'PARKKIHUBI_PUBLIC_API_ENABLED', False):
    urlpatterns.append(url(r'^public/', include(public_urls)))

if getattr(settings, 'PARKKIHUBI_MONITORING_API_ENABLED', False):
    urlpatterns.append(url(r'^monitoring/', include(monitoring_urls)))

if getattr(settings, 'PARKKIHUBI_OPERATOR_API_ENABLED', False):
    urlpatterns.append(url(r'^operator/', include(operator_urls)))

if getattr(settings, 'PARKKIHUBI_ENFORCEMENT_API_ENABLED', False):
    urlpatterns.append(url(r'^enforcement/', include(enforcement_urls)))

urlpatterns.extend([
    url(r'^admin/', admin.site.urls),
])
