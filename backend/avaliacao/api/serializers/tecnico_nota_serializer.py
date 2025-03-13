from rest_framework import serializers


class CriterioNotaSerializer(serializers.Serializer):
    criterio_id = serializers.IntegerField()
    criterio_nome = serializers.CharField()
    nota_media = serializers.FloatField()
    nota_total = serializers.FloatField()
    total_avaliacoes = serializers.IntegerField()


class TecnicoNotaSerializer(serializers.Serializer):
    tecnico_id = serializers.CharField()
    tecnico_nome = serializers.CharField()
    nota_media = serializers.FloatField()
    nota_total = serializers.FloatField()
    total_avaliacoes = serializers.IntegerField()
    criterios = CriterioNotaSerializer(many=True)
