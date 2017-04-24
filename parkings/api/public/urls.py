from django.conf.urls import include, url
from rest_framework.routers import DefaultRouter

from .parking_area import PublicAPIParkingAreaViewSet

router = DefaultRouter()
router.register(r'parking_area', PublicAPIParkingAreaViewSet)

urlpatterns = [
    url(r'^', include(router.urls, namespace='v1')),
]
