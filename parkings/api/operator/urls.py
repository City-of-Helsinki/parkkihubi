from rest_framework.routers import DefaultRouter

from ..url_utils import versioned_url
from .enforcement_domain import EnforcementDomainViewSet
from .parking import OperatorAPIParkingViewSet

router = DefaultRouter()
router.register(r'parking', OperatorAPIParkingViewSet, basename='parking')
router.register(r'enforcement_domain', EnforcementDomainViewSet, basename='enforcement_domain')

app_name = 'operator'
urlpatterns = [
    versioned_url('v1', router.urls),
]
