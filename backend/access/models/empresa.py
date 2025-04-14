import re

from django.core.exceptions import ValidationError
from django.db import models


def validar_cnpj(cnpj):
    cnpj = re.sub(r"[^0-9]", "", cnpj)

    if len(cnpj) != 14:
        raise ValidationError("CNPJ deve conter 14 dígitos")

    if len(set(cnpj)) == 1:
        raise ValidationError("CNPJ inválido")

    # Cálculo primeiro dígito verificador
    soma = 0
    peso = 5
    for i in range(12):
        soma += int(cnpj[i]) * peso
        peso = peso - 1 if peso > 2 else 9

    digito1 = 11 - (soma % 11)
    digito1 = 0 if digito1 > 9 else digito1

    if int(cnpj[12]) != digito1:
        raise ValidationError("CNPJ inválido")

    # Cálculo segundo dígito verificador
    soma = 0
    peso = 6
    for i in range(13):
        soma += int(cnpj[i]) * peso
        peso = peso - 1 if peso > 2 else 9

    digito2 = 11 - (soma % 11)
    digito2 = 0 if digito2 > 9 else digito2

    if int(cnpj[13]) != digito2:
        raise ValidationError("CNPJ inválido")


class Empresa(models.Model):
    nome = models.CharField(max_length=200)
    cnpj = models.CharField(
        max_length=18, unique=True, validators=[validar_cnpj]
    )
    cep = models.CharField(max_length=9)
    telefone = models.CharField(max_length=15)
    numero = models.CharField(max_length=10)
    complemento = models.CharField(max_length=200, blank=True, null=True)
    responsavel = models.ForeignKey(
        "access.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="empresas_responsavel",
    )

    def __str__(self):
        return self.nome

    class Meta:
        db_table = "empresa"
        verbose_name = "Empresa"
        verbose_name_plural = "Empresas"
