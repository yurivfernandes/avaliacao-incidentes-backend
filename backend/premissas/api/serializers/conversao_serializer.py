from rest_framework import serializers

from ...models import Conversao


class ConversaoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Conversao
        fields = ["id", "criterio", "nome", "percentual"]
