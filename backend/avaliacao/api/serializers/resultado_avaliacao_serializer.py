from rest_framework import serializers

from ...models import ResultadoAvaliacao


class ResultadoAvaliacaoSerializer(serializers.ModelSerializer):
    assignment_group = serializers.CharField(
        source="incident.assignment_group_name"
    )
    resolved_by = serializers.CharField(source="incident.resolved_by_name")
    criterio_nome = serializers.CharField(source="criterio.nome")
    incident_number = serializers.CharField(source="incident.number")

    class Meta:
        model = ResultadoAvaliacao
        fields = [
            "id",
            "incident_number",
            "assignment_group",
            "resolved_by",
            "criterio_nome",
            "nota",
            "created_at",
        ]
