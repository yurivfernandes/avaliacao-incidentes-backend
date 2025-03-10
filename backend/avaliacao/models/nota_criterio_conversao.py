from django.db import models

from .nota_criterio_base import NotaCriterioBase


class NotaCriterioConversao(NotaCriterioBase):
    conversao = models.ForeignKey(
        "premissas.Conversao",
        on_delete=models.PROTECT,
        related_name="notas",
    )

    class Meta(NotaCriterioBase.Meta):
        db_table = "avaliacao_nota_criterio_conversao"
        verbose_name = "Nota Critério Conversão"
        verbose_name_plural = "Notas Critérios Conversão"
