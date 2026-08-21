from rest_framework.exceptions import PermissionDenied
from rest_framework.views import exception_handler
from rest_framework.renderers import JSONRenderer

from parkings.api.common import ParkingException
from parkings.api.monitoring.export_parkings import CSVRenderer


def parkings_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is not None:
        if isinstance(exc, ParkingException):
            response.data['code'] = exc.get_codes()
        elif isinstance(exc, PermissionDenied):
            response.data['code'] = 'permission_denied'

        if isinstance(context["request"].accepted_renderer, CSVRenderer):
            context["request"].accepted_renderer = JSONRenderer()

    return response
