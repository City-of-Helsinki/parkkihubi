from django.conf.urls import include, url
from rest_framework.routers import DefaultRouter

from .parking import OperatorAPIParkingViewSet

router = DefaultRouter()
router.register(r'parking', OperatorAPIParkingViewSet)

urlpatterns = [
    url(r'^', include(router.urls, namespace='v1')),
]
