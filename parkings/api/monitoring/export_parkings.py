import csv

from rest_framework import renderers, serializers, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from six import StringIO

from ...models import Parking, ParkingCheck
from .permissions import IsMonitor


class CSVRenderer(renderers.BaseRenderer):
    media_type = "text/csv"
    format = "csv"
    render_style = 'binary'

    def render(self, filters, media_type=None, renderer_context=None):
        time_start = filters["time_start"]
        time_end = filters["time_end"]
        operators = filters.get("operators")
        payment_zones = filters.get("payment_zones")
        parking_check = filters.get("parking_check")

        kwargs = {
            "time_start__lte": time_end,
            "time_end__gte": time_start,
        }

        if payment_zones:
            kwargs["zone__code__in"] = payment_zones
        if operators:
            kwargs["operator__id__in"] = operators

        parkings = (
            Parking.objects
            .filter(**kwargs)
            .order_by("-time_start")
            .prefetch_related("operator", "zone")
        )

        if parking_check:
            parking_check_parking_ids = (
                ParkingCheck.objects
                .filter(found_parking__id__in=parkings)
                .order_by("found_parking")
                .values_list("found_parking")
                .distinct()
            )
            parkings = parkings.filter(id__in=parking_check_parking_ids)

        buffer = StringIO()
        writer = csv.writer(buffer)

        for park in parkings:
            writer.writerow([
                ("%s, %s" % (park.location.x, park.location.y)) if park.location else " ",
                park.terminal_number,
                park.time_start.strftime("%d.%m.%Y %H.%M"),
                park.time_end.strftime("%d.%m.%Y %H.%M"),
                park.created_at.strftime("%d.%m.%Y %H.%M"),
                park.modified_at.strftime("%d.%m.%Y %H.%M"),
                park.operator.name,
                park.zone.name
            ])

        return buffer.getvalue()


class ExportFilterSerializer(serializers.Serializer):
    operators = serializers.ListSerializer(child=serializers.CharField(), required=False)
    payment_zones = serializers.ListSerializer(child=serializers.CharField(), required=False)
    parking_check = serializers.BooleanField(required=False)
    time_start = serializers.DateTimeField(
        input_formats=["%d.%m.%Y %H.%M"],
    )
    time_end = serializers.DateTimeField(
        input_formats=["%d.%m.%Y %H.%M"],
    )

    def validate(self, data):
        time_start = data.get("time_start")
        time_end = data.get("time_end")

        if not time_start or not time_end:
            raise serializers.ValidationError("You must provde start date and end date")
        elif time_start > time_end:
            raise serializers.ValidationError("End date must be after start date.")

        return data


class ExportViewSet(viewsets.ViewSet):
    queryset = Parking.objects.all()
    permission_classes = [IsMonitor, ]

    @action(detail=False, methods=['post'], renderer_classes=[CSVRenderer])
    def download(self, request):
        serializer = ExportFilterSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            time_start = serializer.validated_data["time_start"]
            time_end = serializer.validated_data["time_end"]
            file_name = "parkings_{}_{}.csv".format(
                time_start.date(), time_end.date()
            )
            response = Response(
                serializer.validated_data,
                content_type="text/csv",
                headers={"X-Suggested-Filename": file_name}
            )
            response['Content-Disposition'] = 'attachment; filename="%s"' % file_name

            return response
