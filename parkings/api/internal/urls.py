from django.conf.urls import include, url
from rest_framework.routers import DefaultRouter

from .parking import InternalAPIParkingViewSet

router = DefaultRouter()
router.register(r'parking', InternalAPIParkingViewSet)

urlpatterns = [
    url(r'^', include(router.urls, namespace='v1')),
]
