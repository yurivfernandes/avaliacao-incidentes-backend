from rest_framework import serializers

from ...models import Empresa


class EmpresaCreateSerializer(serializers.ModelSerializer):
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
        ]

    def validate_cnpj(self, value):
        # Remove caracteres especiais do CNPJ
        cnpj = "".join(filter(str.isdigit, value))

        # Verifica se já existe uma empresa com este CNPJ
        if Empresa.objects.filter(cnpj=cnpj).exists():
            raise serializers.ValidationError(
                "Já existe uma empresa cadastrada com este CNPJ"
            )

        return value

    def validate_telefone(self, value):
        # Remove caracteres especiais do telefone
        telefone = "".join(filter(str.isdigit, value))

        if len(telefone) < 10 or len(telefone) > 11:
            raise serializers.ValidationError(
                "Telefone deve ter 10 ou 11 dígitos"
            )

        return value
