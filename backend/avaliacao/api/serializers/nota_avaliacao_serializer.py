from rest_framework import serializers

from ...models import NotaCriterioBooleano, NotaCriterioConversao


class NotaAvaliacaoSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    criterio = serializers.IntegerField(source="criterio.id")
    criterio_nome = serializers.CharField(source="criterio.nome")
    tipo = serializers.CharField(source="criterio.tipo")
    valor = serializers.SerializerMethodField()

    def get_valor(self, obj):
        if hasattr(obj, "valor"):
            return obj.valor
        return obj.conversao.nome if hasattr(obj, "conversao") else None
