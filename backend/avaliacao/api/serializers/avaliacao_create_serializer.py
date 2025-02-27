from dw_analytics.models import Incident
from rest_framework import serializers

from ...models import Avaliacao


class AvaliacaoCreateSerializer(serializers.ModelSerializer):
    incident_id = serializers.IntegerField()

    class Meta:
        model = Avaliacao
        fields = [
            "incident_id",
            "is_contrato_lancado",
            "is_horas_lancadas",
            "is_has_met_first_response_target",
            "is_resolution_target",
            "is_atualizaca_logs_correto",
            "is_ticket_encerrado_corretamente",
            "is_descricao_troubleshooting",
            "is_cliente_notificado",
            "is_category_correto",
        ]

    def validate_incident_id(self, value):
        try:
            Incident.objects.get(id=value)
        except Incident.DoesNotExist:
            raise serializers.ValidationError("Incident não encontrado")
        return value

    def create(self, validated_data):
        incident_id = validated_data.pop('incident_id')
        incident = Incident.objects.get(id=incident_id)
        return Avaliacao.objects.create(incident=incident, **validated_data)
