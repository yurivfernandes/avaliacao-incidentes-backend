from rest_framework import serializers

from ...models import Empresa


class EmpresaSerializer(serializers.ModelSerializer):
    responsavel_nome = serializers.SerializerMethodField()

    class Meta:
        model = Empresa
        fields = [
            "id",
            "nome",
            "cnpj",
            "cep",
            "telefone",
            "numero",
            "complemento",
            "responsavel",
            "responsavel_nome",
        ]

    def get_responsavel_nome(self, obj):
        return obj.responsavel.full_name if obj.responsavel else None
