from django.conf.urls import include, url
from rest_framework import permissions
from rest_framework.routers import APIRootView, DefaultRouter

from .parking_area import PublicAPIParkingAreaViewSet
from .parking_area_statistics import PublicAPIParkingAreaStatisticsViewSet


class PublicApiRootView(APIRootView):
    permission_classes = [permissions.AllowAny]


class Router(DefaultRouter):
    APIRootView = PublicApiRootView


router = Router()
router.register(
    r'parking_area',
    PublicAPIParkingAreaViewSet, basename='parkingarea')
router.register(
    r'parking_area_statistics',
    PublicAPIParkingAreaStatisticsViewSet, basename='parkingareastatistics')

urlpatterns = [
    url(r'^', include(router.urls, namespace='v1')),
]
