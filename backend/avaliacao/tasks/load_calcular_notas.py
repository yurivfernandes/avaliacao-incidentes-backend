import re

import polars as pl
from app.utils.pipiline import Pipeline
from celery import shared_task
from django.db import transaction
from django.db.models import (
    Case,
    ExpressionWrapper,
    F,
    FloatField,
    Q,
    QuerySet,
    Value,
    When,
)
from django.utils import timezone
from django.utils.datetime_safe import datetime
from premissas.models import Criterios

from ..models import (
    Avaliacao,
    NotaCriterioBooleano,
    NotaCriterioConversao,
    ResultadoAvaliacao,
)


class LoadCalcularNotas(Pipeline):
    """Extrai, transforma e carrega as notas calculadas das avaliações."""

    def __init__(self, **kwargs) -> None:
        super().__init__()
        self.avaliacao_id = kwargs.get("avaliacao_id")
        self.assignment_group = kwargs.get(
            "assignment_group"
        )  # Novo parâmetro
        data_referencia = kwargs.get("data_referencia")

        if not re.match(r"^\d{4}-(?:0[1-9]|1[0-2])$", data_referencia):
            raise ValueError(
                "data_referencia deve estar no formato YYYY-MM (exemplo: 2024-01)"
            )

        # Formatar a data de referência para o primeiro dia do mês às 00:00
        self.data_referencia = datetime.strptime(
            f"{data_referencia}-01 00:00:00", "%Y-%m-%d %H:%M:%S"
        )

    def get_avaliacao_queryset(self) -> QuerySet:
        """Retorna o queryset de [Avaliacao]"""
        # Obter início e fim do mês de referência
        data_ref = self.data_referencia.replace(
            day=1, hour=0, minute=0, second=0, microsecond=0
        )

        queryset = Avaliacao.objects.filter(
            incident__closed_at__year=data_ref.year,
            incident__closed_at__month=data_ref.month,
        )

        if self.avaliacao_id:
            queryset = queryset.filter(id=self.avaliacao_id)

        if self.assignment_group:
            queryset = queryset.filter(
                incident__assignment_group=self.assignment_group
            )

        return queryset

    def get_criterios_queryset(self) -> QuerySet:
        """Retorna o queryset de [Criterios]"""
        return Criterios.objects.filter(ativo=True)

    def get_notas_queryset(self) -> QuerySet:
        """Retorna o queryset com as notas calculadas dos dois tipos de critérios"""
        # Obter os IDs das avaliações do período
        avaliacoes_ids = self.get_avaliacao_queryset().values_list(
            "id", flat=True
        )

        # Criar filtro base
        base_filter = {"avaliacao_id__in": avaliacoes_ids}
        if self.avaliacao_id:
            base_filter["avaliacao_id"] = self.avaliacao_id

        notas_booleanas = (
            NotaCriterioBooleano.objects.filter(**base_filter)
            .annotate(
                nota_calculada=Case(
                    When(valor=True, then=F("criterio__peso")),
                    default=Value(0),
                    output_field=FloatField(),
                )
            )
            .values("criterio_id", "nota_calculada", "avaliacao_id")
        )

        notas_conversao = (
            NotaCriterioConversao.objects.filter(**base_filter)
            .annotate(
                nota_calculada=ExpressionWrapper(
                    F("criterio__peso") * F("conversao__percentual") / 100.0,
                    output_field=FloatField(),
                )
            )
            .values("criterio_id", "nota_calculada", "avaliacao_id")
        )

        return notas_booleanas.union(notas_conversao)

    def run(self) -> dict:
        self.extract_transform_dataset()
        self.load()
        return self.log

    def extract_transform_dataset(self) -> None:
        # Garantir que a data seja sempre o primeiro dia do mês às 00:00
        data_ref = self.data_referencia.replace(
            day=1, hour=0, minute=0, second=0, microsecond=0
        )

        self.dataset = self._notas_dataset.select(
            [
                pl.col("avaliacao_id"),
                pl.col("criterio_id"),
                pl.col("nota_calculada").alias("nota"),
                pl.lit(data_ref.strftime("%Y-%m-%d %H:%M:%S")).alias(
                    "data_referencia"
                ),
            ]
        )

    @property
    def _notas_dataset(self) -> pl.DataFrame:
        """Retorna um dataset com as notas dos critérios já calculadas"""
        qs = self.get_notas_queryset()
        return pl.DataFrame(data=list(qs))

    @property
    def _criterios_dataset(self) -> pl.DataFrame:
        """Retorna um dataset com os critérios"""
        qs = self.get_criterios_queryset().values(
            "id",
            "tipo",
            "peso",
        )
        return pl.DataFrame(data=list(qs))

    @transaction.atomic
    def load(self) -> None:
        self._delete()
        self._save()

    def _delete(self):
        # Truncar a data até o mês para o filtro
        data_ref = self.data_referencia.replace(
            day=1, hour=0, minute=0, second=0, microsecond=0
        )

        filters = {"data_referencia": data_ref}
        if self.avaliacao_id:
            filters["avaliacao_id"] = self.avaliacao_id

        n_deleted, __ = ResultadoAvaliacao.objects.filter(**filters).delete()
        self.log["n_deleted"] = n_deleted

    def _save(self):
        if self.dataset.is_empty():
            return

        objs = [ResultadoAvaliacao(**vals) for vals in self.dataset.to_dicts()]
        bulk = ResultadoAvaliacao.objects.bulk_create(
            objs=objs, batch_size=1000
        )
        self.log["n_inserted"] = len(bulk)


# Comentar a task do Celery por enquanto


@shared_task(
    name="avaliacao.load_calcular_notas",
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=5,
    retry_kwargs={"max_retries": 3},
)
def load_calcular_notas_async(
    self, avaliacao_id: int, data_referencia: str
) -> dict:
    with LoadCalcularNotas(
        avaliacao_id=avaliacao_id, data_referencia=data_referencia
    ) as task:
        log = task.run()
    return log
