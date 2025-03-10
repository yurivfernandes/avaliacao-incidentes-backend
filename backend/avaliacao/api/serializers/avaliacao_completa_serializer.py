from avaliacao.models import Avaliacao
from rest_framework import serializers


class CriterioSerializer(serializers.Serializer):
    tipo = serializers.ChoiceField(choices=["booleano", "conversao"])
    criterio_id = serializers.IntegerField()
    valor = serializers.BooleanField(
        required=False
    )  # para NotaCriterioBooleano
    conversao_id = serializers.IntegerField(
        required=False
    )  # para NotaCriterioConversao

    def validate(self, data):
        if data["tipo"] == "booleano" and "valor" not in data:
            raise serializers.ValidationError(
                "Campo 'valor' é obrigatório para critério booleano"
            )
        if data["tipo"] == "conversao" and "conversao_id" not in data:
            raise serializers.ValidationError(
                "Campo 'conversao_id' é obrigatório para critério de conversão"
            )
        return data


class AvaliacaoCompletaSerializer(serializers.ModelSerializer):
    criterios = CriterioSerializer(many=True, write_only=True)

    class Meta:
        model = Avaliacao
        fields = ["id", "incident", "criterios"]

    def create(self, validated_data):
        criterios = validated_data.pop(
            "criterios"
        )  # Remove criterios antes de criar a avaliação
        avaliacao = super().create(validated_data)
        return avaliacao
