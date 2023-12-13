from parkings.api.auth import drf_jwt_2fa_urls

from ..url_utils import versioned_url

app_name = 'auth'
urlpatterns = [
    versioned_url('v1', drf_jwt_2fa_urls),
]
