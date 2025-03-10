from rest_framework import serializers

from ...models import NotaCriterioBooleano, NotaCriterioConversao


class NotaCriterioBooleanoSerializer(serializers.ModelSerializer):
    criterio_nome = serializers.CharField(source="criterio.nome")

    class Meta:
        model = NotaCriterioBooleano
        fields = ["criterio_nome", "valor", "created_at"]


class NotaCriterioConversaoSerializer(serializers.ModelSerializer):
    criterio_nome = serializers.CharField(source="criterio.nome")
    valor_convertido = serializers.FloatField(source="conversao.percentual")

    class Meta:
        model = NotaCriterioConversao
        fields = ["criterio_nome", "valor_convertido", "created_at"]
