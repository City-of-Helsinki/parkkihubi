from django.conf.urls import include, url
from rest_framework.routers import DefaultRouter

from .valid_parking import ValidParkingViewSet

router = DefaultRouter()
router.register('valid_parking', ValidParkingViewSet,
                base_name='valid_parking')

urlpatterns = [
    url(r'^', include(router.urls, namespace='v1')),
]
