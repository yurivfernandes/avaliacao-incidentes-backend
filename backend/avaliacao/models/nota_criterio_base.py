from django.db import models


class NotaCriterioBase(models.Model):
    avaliacao = models.ForeignKey(
        "avaliacao.Avaliacao",
        on_delete=models.CASCADE,
    )
    criterio = models.ForeignKey(
        "premissas.Criterios",
        on_delete=models.PROTECT,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
        unique_together = ["avaliacao", "criterio"]
