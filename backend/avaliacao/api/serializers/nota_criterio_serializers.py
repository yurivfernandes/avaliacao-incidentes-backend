from premissas.models import Criterios
from rest_framework import serializers

from ...models import NotaCriterioBooleano, NotaCriterioConversao


class NotaCriterioBooleanoSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotaCriterioBooleano
        fields = ["id", "avaliacao", "criterio", "valor"]
        read_only_fields = ["avaliacao"]

    def validate_criterio(self, value):
        if not value.tipo == "booleano":
            raise serializers.ValidationError(
                "Este critério não é do tipo booleano"
            )
        return value


class NotaCriterioConversaoSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotaCriterioConversao
        fields = ["id", "avaliacao", "criterio", "conversao"]
        read_only_fields = ["avaliacao"]

    def validate_criterio(self, value):
        if not value.tipo == "conversao":
            raise serializers.ValidationError(
                "Este critério não é do tipo conversão"
            )
        return value
