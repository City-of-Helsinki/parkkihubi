from rest_framework import mixins, serializers
from rest_framework.viewsets import GenericViewSet

from parkings.models import EnforcementDomain, PaymentZone

from .permissions import IsOperator


class PaymentZoneSerializer(serializers.ModelSerializer):
    domain = serializers.SlugRelatedField(
        slug_field='code', queryset=EnforcementDomain.objects.all())

    class Meta:
        model = PaymentZone
        fields = ['domain', 'code', 'name']


class PaymentZoneViewSet(mixins.ListModelMixin, GenericViewSet):
    permission_classes = [IsOperator]
    serializer_class = PaymentZoneSerializer
    queryset = PaymentZone.objects.all()
