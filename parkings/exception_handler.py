from rest_framework.exceptions import PermissionDenied
from rest_framework.views import exception_handler

from parkings.api.common import ParkingException


def parkings_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is not None:
        if isinstance(exc, ParkingException):
            response.data['code'] = exc.get_codes()
        elif isinstance(exc, PermissionDenied):
            response.data['code'] = 'permission_denied'

    return response
