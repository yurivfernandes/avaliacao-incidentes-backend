from django.db import models
from dw_analytics.models import AssignmentGroup


class Premissas(models.Model):
    assignment = models.OneToOneField(
        AssignmentGroup,
        on_delete=models.PROTECT,
        related_name="premissas",
        help_text="Assignment Group relacionado",
    )
    qtd_incidents = models.IntegerField(
        help_text="Quantidade de incidentes a serem sorteados"
    )
    meta_mensal = models.IntegerField(
        default=70, help_text="Meta mensal dos analistas em pontos"
    )

    def __str__(self):
        return f"{self.assignment.dv_assignment_group} - {self.qtd_incidents} incidentes"

    class Meta:
        db_table = "d_premissas"
        verbose_name = "Premissa"
        verbose_name_plural = "Premissas"
