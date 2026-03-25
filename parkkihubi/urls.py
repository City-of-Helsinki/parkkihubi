from django.conf import settings
from django.contrib import admin
from django.urls import include, re_path

from parkings.api.auth import urls as auth_urls
from parkings.api.enforcement import urls as enforcement_urls
from parkings.api.monitoring import urls as monitoring_urls
from parkings.api.operator import urls as operator_urls
from parkings.api.public import urls as public_urls

urlpatterns = [
   re_path(r'^auth/', include(auth_urls)),
]

if getattr(settings, 'PARKKIHUBI_PUBLIC_API_ENABLED', False):
    urlpatterns.append(re_path(r'^public/', include(public_urls)))

if getattr(settings, 'PARKKIHUBI_MONITORING_API_ENABLED', False):
    urlpatterns.append(re_path(r'^monitoring/', include(monitoring_urls)))

if getattr(settings, 'PARKKIHUBI_OPERATOR_API_ENABLED', False):
    urlpatterns.append(re_path(r'^operator/', include(operator_urls)))

if getattr(settings, 'PARKKIHUBI_ENFORCEMENT_API_ENABLED', False):
    urlpatterns.append(re_path(r'^enforcement/', include(enforcement_urls)))

urlpatterns.extend([
    re_path(r'^admin/', admin.site.urls),
])
