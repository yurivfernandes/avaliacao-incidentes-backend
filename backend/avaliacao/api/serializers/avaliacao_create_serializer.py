from dw_analytics.models import Incident
from rest_framework import serializers

from ...models import Avaliacao


class AvaliacaoCreateSerializer(serializers.ModelSerializer):
    incident_id = serializers.IntegerField()

    class Meta:
        model = Avaliacao
        fields = ["incident_id"]

    def validate_incident_id(self, value):
        try:
            Incident.objects.get(id=value)
        except Incident.DoesNotExist:
            raise serializers.ValidationError("Incident não encontrado")
        return value

    def create(self, validated_data):
        incident_id = validated_data.pop("incident_id")
        incident = Incident.objects.get(id=incident_id)

        avaliacao = Avaliacao.objects.create(
            incident=incident, **validated_data
        )

        return avaliacao
