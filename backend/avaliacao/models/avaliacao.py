from django.contrib.auth import get_user_model
from django.db import models
from dw_analytics.models import Incident


class Avaliacao(models.Model):
    incident = models.ForeignKey(
        Incident,
        on_delete=models.PROTECT,
        related_name="avaliacoes",
        help_text="Incidente avaliado",
    )
    user = models.ForeignKey(
        get_user_model(),
        on_delete=models.PROTECT,
        related_name="avaliacoes",
        help_text="Usuário que realizou a avaliação",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Data de criação do registro",
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Data da última atualização",
    )

    def __str__(self):
        return f"Avaliação {self.incident.number}"

    class Meta:
        db_table = "f_avaliacao"
        verbose_name = "Avaliação"
        verbose_name_plural = "Avaliações"
