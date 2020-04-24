from django.conf.urls import url
from rest_framework.routers import DefaultRouter

from ..url_utils import versioned_url
from .check_parking import CheckParking
from .enforcement_permit import (
    EnforcementActivePermitByExternalIdViewSet, EnforcementPermitSeriesViewSet,
    EnforcementPermitViewSet)
from .operator import OperatorViewSet
from .valid_parking import ValidParkingViewSet
from .valid_permit_item import ValidPermitItemViewSet


class Router(DefaultRouter):
    def get_urls(self):
        urls = super().get_urls()
        return urls + [
            url(r"^check_parking/$", CheckParking.as_view(), name="check_parking"),
        ]

    def get_api_root_view(self, *args, **kwargs):
        view = super().get_api_root_view(*args, **kwargs)
        view.initkwargs['api_root_dict']['check_parking'] = 'check_parking'
        return view


router = Router()
router.register('operator', OperatorViewSet, basename='operator')
router.register('permit', EnforcementPermitViewSet, basename='permit')
router.register('active_permit_by_external_id',
                EnforcementActivePermitByExternalIdViewSet, basename='activepermit')
router.register('permitseries', EnforcementPermitSeriesViewSet, basename='permitseries')
router.register('valid_parking', ValidParkingViewSet,
                basename='valid_parking')
router.register('valid_permit_item', ValidPermitItemViewSet, basename='valid_permit_item')

app_name = 'enforcement'
urlpatterns = [
    versioned_url('v1', router.urls),
]
