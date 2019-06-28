from django.conf.urls import include, url
from rest_framework.routers import DefaultRouter

from .operator import OperatorViewSet
from .permit import (
    ActivePermitByExternalIdViewSet, PermitSeriesViewSet, PermitViewSet)
from .valid_parking import ValidParkingViewSet

router = DefaultRouter()
router.register('operator', OperatorViewSet, basename='operator')
router.register('permit', PermitViewSet, basename='permit')
router.register('active_permit_by_external_id',
                ActivePermitByExternalIdViewSet, basename='activepermit')
router.register('permitseries', PermitSeriesViewSet, basename='permitseries')
router.register('valid_parking', ValidParkingViewSet,
                basename='valid_parking')

urlpatterns = [
    url(r'^', include(router.urls, namespace='v1')),
]
