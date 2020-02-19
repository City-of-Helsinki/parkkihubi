from rest_framework.routers import DefaultRouter

from ..url_utils import versioned_url
from .parking import OperatorAPIParkingViewSet
from .permit import (
    OperatorActivePermitByExternalIdViewSet, OperatorPermitSeriesViewSet,
    OperatorPermittedPermitAreaViewSet, OperatorPermitViewSet)

router = DefaultRouter()
router.register(r'parking', OperatorAPIParkingViewSet, basename='parking')
router.register(r'permitseries', OperatorPermitSeriesViewSet, basename='permitseries')
router.register(r'permit', OperatorPermitViewSet, basename='permit')
router.register(r'activepermit', OperatorActivePermitByExternalIdViewSet, basename='activepermit')
router.register(r'permit_area', OperatorPermittedPermitAreaViewSet, basename='permitarea')

app_name = 'operator'
urlpatterns = [
    versioned_url('v1', router.urls),
]
