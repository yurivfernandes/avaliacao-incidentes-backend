from rest_framework import serializers

from ...models import NotaCriterioBooleano, NotaCriterioConversao


class NotaCriterioBooleanoSerializer(serializers.ModelSerializer):
    criterio_nome = serializers.CharField(
        source="criterio.nome", read_only=True
    )
    valor = serializers.BooleanField()

    class Meta:
        model = NotaCriterioBooleano
        fields = ["id", "criterio_nome", "valor", "criterio"]
        read_only_fields = ["criterio_nome"]


class NotaCriterioConversaoSerializer(serializers.ModelSerializer):
    criterio_nome = serializers.CharField(
        source="criterio.nome", read_only=True
    )
    nome_conversao = serializers.CharField(
        source="conversao.nome", read_only=True
    )

    class Meta:
        model = NotaCriterioConversao
        fields = [
            "id",
            "criterio_nome",
            "nome_conversao",
            "criterio",
            "conversao",
        ]
        read_only_fields = ["criterio_nome", "nome_conversao"]
