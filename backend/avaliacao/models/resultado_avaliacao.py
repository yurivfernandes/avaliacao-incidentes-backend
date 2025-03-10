from django.db import models
from premissas.models import Criterios

from .avaliacao import Avaliacao


class ResultadoAvaliacao(models.Model):
    avaliacao = models.ForeignKey(
        Avaliacao,
        on_delete=models.PROTECT,
        related_name="resultado_avaliacao",
        help_text="FK da Avaliação",
    )
    criterio = models.ForeignKey(
        Criterios,
        on_delete=models.PROTECT,
        related_name="resultado_avaliacao",
        help_text="Critério avaliado",
    )
    nota = models.FloatField(help_text="Nota atribuída ao critério")
    data_referencia = models.DateTimeField(
        help_text="Data de referência para a avaliação"
    )
    created_at = models.DateTimeField(
        auto_now_add=True, help_text="Data de criação"
    )

    class Meta:
        db_table = "f_resultado_avaliacao"
        verbose_name = "Resultado da Nota da Avaliação"
        verbose_name_plural = "Notas das Avaliações"
        unique_together = ["avaliacao", "criterio"]
