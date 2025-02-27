from rest_framework import serializers

from ...models import Avaliacao


class AvaliacaoCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Avaliacao
        fields = [
            "incident",
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
