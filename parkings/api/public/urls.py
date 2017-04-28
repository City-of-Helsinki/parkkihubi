from django.conf.urls import include, url
from rest_framework.routers import DefaultRouter

from .parking_area import PublicAPIParkingAreaViewSet
from .parking_area_statistics import PublicAPIParkingAreaStatisticsViewSet

router = DefaultRouter()
router.register(r'parking_area', PublicAPIParkingAreaViewSet, base_name='parkingarea')
router.register(r'parking_area_statistics', PublicAPIParkingAreaStatisticsViewSet, base_name='parkingareastatistics')

urlpatterns = [
    url(r'^', include(router.urls, namespace='v1')),
]
