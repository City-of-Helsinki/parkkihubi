from django.conf.urls import include, url
from rest_framework.routers import DefaultRouter

from .operator import OperatorViewSet
from .permit import (
    ActivePermitByExternalIdViewSet, PermitSeriesViewSet, PermitViewSet)
from .valid_parking import ValidParkingViewSet

router = DefaultRouter()
router.register('operator', OperatorViewSet, base_name='operator')
router.register('permit', PermitViewSet, base_name='permit')
router.register('active_permit_by_external_id',
                ActivePermitByExternalIdViewSet, base_name='activepermit')
router.register('permitseries', PermitSeriesViewSet, base_name='permitseries')
router.register('valid_parking', ValidParkingViewSet,
                base_name='valid_parking')

urlpatterns = [
    url(r'^', include(router.urls, namespace='v1')),
]
