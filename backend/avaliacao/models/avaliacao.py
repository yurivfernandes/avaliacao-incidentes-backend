from django.contrib.auth import get_user_model
from django.db import models
from dw_analytics.models import Incident
from premissas.models import Criterios

from .nota_criterio_booleano import NotaCriterioBooleano


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

    def _converter_valor_sla(self, campo: str, valor: bool) -> bool:
        """
        Converte o valor do SLA do ServiceNow para o formato correto da avaliação.
        No ServiceNow: True = SLA estourado, False = SLA dentro do prazo
        Na avaliação: True = SLA atendido, False = SLA não atendido
        """
        if campo.startswith("sla_"):
            return not valor  # inverte o valor para campos de SLA
        return valor

    def create_servicenow_notes(self):
        """Cria notas baseadas nos campos do ServiceNow"""
        criterios_servicenow = Criterios.objects.filter(
            field_service_now__isnull=False,
            tipo="boolean",
            ativo=True,
        )

        for criterio in criterios_servicenow:
            valor_sn = getattr(self.incident, criterio.field_service_now, None)

            if valor_sn is not None:
                # Converte o valor se for campo de SLA
                valor_convertido = self._converter_valor_sla(
                    criterio.field_service_now, bool(valor_sn)
                )

                NotaCriterioBooleano.objects.create(
                    avaliacao=self,
                    criterio=criterio,
                    valor=valor_convertido,
                )

    def save(self, *args, **kwargs):
        is_new = not self.pk
        super().save(*args, **kwargs)
        if is_new:
            self.create_servicenow_notes()

    def __str__(self):
        return f"Avaliação {self.incident.number}"

    class Meta:
        db_table = "f_avaliacao"
        verbose_name = "Avaliação"
        verbose_name_plural = "Avaliações"
