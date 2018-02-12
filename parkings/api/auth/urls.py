import drf_jwt_2fa.urls
from django.conf.urls import include, url

v1_urlpatterns = [
    url(r'^', include(drf_jwt_2fa.urls, namespace='auth')),
]

urlpatterns = [
    url(r'^', include(v1_urlpatterns, namespace='v1')),
]
