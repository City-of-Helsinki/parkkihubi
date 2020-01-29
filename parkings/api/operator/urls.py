from rest_framework.routers import DefaultRouter

from ..url_utils import versioned_url
from .parking import OperatorAPIParkingViewSet

router = DefaultRouter()
router.register(r'parking', OperatorAPIParkingViewSet, basename='parking')

app_name = 'operator'
urlpatterns = [
    versioned_url('v1', router.urls),
]
