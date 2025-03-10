from django.db import models

from .nota_criterio_base import NotaCriterioBase


class NotaCriterioBooleano(NotaCriterioBase):
    valor = models.BooleanField(
        help_text="Valor booleano (True/False)",
    )

    class Meta(NotaCriterioBase.Meta):
        db_table = "avaliacao_nota_criterio_booleano"
        verbose_name = "Nota Critério Booleano"
        verbose_name_plural = "Notas Critérios Booleanos"
