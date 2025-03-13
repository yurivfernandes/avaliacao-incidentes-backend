from datetime import datetime

from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied
from django.db.models import Avg, Count, F, Sum
from django.db.models.functions import ExtractYear
from dw_analytics.models import AssignmentGroup
from premissas.models import Premissas
from rest_framework import generics
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from ...models import ResultadoAvaliacao


class RankingAnualView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        start_date = self.request.query_params.get("start_date")
        end_date = self.request.query_params.get("end_date")
        assignment_group = self.request.query_params.get("assignment_group")

        if not all([start_date, end_date, assignment_group]):
            raise ValidationError(
                {"error": "Parâmetros obrigatórios ausentes"}
            )

        try:
            start_date = datetime.strptime(start_date, "%Y-%m-%d")
            end_date = datetime.strptime(end_date, "%Y-%m-%d")
        except ValueError:
            raise ValidationError({"error": "Formato de data inválido"})

        queryset = ResultadoAvaliacao.objects.filter(
            data_referencia__range=[start_date, end_date],
            avaliacao__incident__assignment_group=assignment_group,
        )

        user = self.request.user
        if not user.is_staff:
            if user.is_gestor:
                user_groups = user.assignment_groups.values_list(
                    "id", flat=True
                )
                if int(assignment_group) not in user_groups:
                    raise PermissionDenied()
            else:
                queryset = queryset.filter(
                    avaliacao__incident__resolved_by=str(user.id)
                )

        ranking = (
            queryset.annotate(
                ano=ExtractYear("data_referencia"),
                tecnico_id=F("avaliacao__incident__resolved_by"),
            )
            .values("ano", "tecnico_id")
            .annotate(
                media=Sum("nota")
                / Count(
                    "avaliacao", distinct=True
                ),  # Corrigido o cálculo da média
                total=Sum("nota"),
                total_avaliacoes=Count("avaliacao", distinct=True),
            )
            .order_by("ano", "-media")
        )

        User = get_user_model()
        tecnicos = {
            str(u.id): f"{u.first_name} {u.last_name}".strip() or u.username
            for u in User.objects.all()
        }

        try:
            premissa = Premissas.objects.get(assignment_id=assignment_group)
            meta_mensal = premissa.meta_mensal
        except Premissas.DoesNotExist:
            meta_mensal = None

        resultado = {}
        for item in ranking:
            ano = str(item["ano"])
            if ano not in resultado:
                resultado[ano] = []

            resultado[ano].append(
                {
                    "tecnico_id": item["tecnico_id"],
                    "tecnico_nome": tecnicos.get(
                        item["tecnico_id"], "Desconhecido"
                    ),
                    "media": round(item["media"], 2),
                    "total": round(item["total"], 2),
                    "total_avaliacoes": item["total_avaliacoes"],
                    "posicao": len(resultado[ano]) + 1,
                    "meta_atingida": item["media"] >= meta_mensal
                    if meta_mensal
                    else False,
                }
            )

        return Response(
            [
                {"ano": ano, "tecnicos": dados}
                for ano, dados in resultado.items()
            ]
        )
