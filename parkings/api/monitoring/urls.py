from django.conf.urls import include, url
from rest_framework.routers import DefaultRouter

from .region import RegionViewSet
from .region_statistics import RegionStatisticsViewSet

router = DefaultRouter()
router.register(r'region', RegionViewSet, base_name='region')
router.register(r'region_statistics', RegionStatisticsViewSet,
                base_name='regionstatistics')

urlpatterns = [
    url(r'^', include(router.urls, namespace='v1')),
]
