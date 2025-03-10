from rest_framework import serializers

from ...models import Criterios


class CriterioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Criterios
        fields = [
            "id",
            "nome",
            "tipo",
            "ativo",
            "peso",
            "premissa",
            "field_service_now",
        ]
