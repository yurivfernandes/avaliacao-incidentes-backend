from datetime import datetime

from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied
from django.db.models import Count, F, Sum
from django.db.models.functions import TruncMonth
from dw_analytics.models import AssignmentGroup
from premissas.models import Premissas
from rest_framework import generics
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from ...models import ResultadoAvaliacao
from ..serializers import NotaPorTecnicoSerializer


class NotaPorTecnicoView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = NotaPorTecnicoSerializer

    def get(self, request, *args, **kwargs):
        data = self.get_dashboard_data()
        return Response(data)

    def get_dashboard_data(self):
        user = self.request.user

        # Validação dos parâmetros obrigatórios
        start_date = self.request.query_params.get("start_date")
        end_date = self.request.query_params.get("end_date")
        assignment_group = self.request.query_params.get("assignment_group")

        if not all([start_date, end_date, assignment_group]):
            missing_params = []
            if not start_date:
                missing_params.append("start_date")
            if not end_date:
                missing_params.append("end_date")
            if not assignment_group:
                missing_params.append("assignment_group")

            raise ValidationError(
                {
                    "error": "Parâmetros obrigatórios ausentes",
                    "missing_params": missing_params,
                }
            )

        try:
            start_date = datetime.strptime(start_date, "%Y-%m-%d")
            end_date = datetime.strptime(end_date, "%Y-%m-%d")
        except ValueError:
            raise ValidationError(
                {"error": "Formato de data inválido. Use YYYY-MM-DD"}
            )

        queryset = ResultadoAvaliacao.objects.select_related(
            "avaliacao__incident", "criterio"
        ).filter(
            data_referencia__range=[start_date, end_date],
            avaliacao__incident__assignment_group=assignment_group,
        )

        if not user.is_staff:
            if user.is_gestor:
                user_groups = user.assignment_groups.values_list(
                    "id", flat=True
                )
                if int(assignment_group) not in user_groups:
                    raise PermissionDenied(
                        "Você não tem permissão para acessar este grupo"
                    )
            else:
                queryset = queryset.filter(
                    avaliacao__incident__resolved_by=str(user.id)
                )

        resultados = (
            queryset.annotate(
                mes=TruncMonth("data_referencia"),
                tecnico_id=F("avaliacao__incident__resolved_by"),
                grupo_id=F("avaliacao__incident__assignment_group"),
            )
            .values(
                "mes",
                "tecnico_id",
                "grupo_id",
                "criterio__id",
                "criterio__nome",
            )
            .annotate(
                nota_total=Sum("nota"),
                total_avaliacoes=Count("avaliacao", distinct=True),
            )
            .order_by("mes", "grupo_id", "tecnico_id", "criterio__id")
        )

        # Calcular total de tickets por mês e grupo
        total_tickets_por_grupo = (
            queryset.annotate(
                mes=TruncMonth("data_referencia"),
                grupo_id=F("avaliacao__incident__assignment_group"),
            )
            .values("mes", "grupo_id")
            .annotate(total_tickets=Count("avaliacao", distinct=True))
        )

        # Criar um dicionário para fácil acesso ao total de tickets
        tickets_map = {
            f"{t['mes'].strftime('%m/%Y')}_{t['grupo_id']}": t["total_tickets"]
            for t in total_tickets_por_grupo
        }

        grupos = AssignmentGroup.objects.all()
        grupo_map = {str(g.id): g.dv_assignment_group for g in grupos}

        User = get_user_model()
        tecnicos = User.objects.filter(
            id__in=set(r["tecnico_id"] for r in resultados if r["tecnico_id"])
        )
        tecnico_map = {
            str(t.id): f"{t.first_name} {t.last_name}".strip() or t.username
            for t in tecnicos
        }

        resultado_final = []

        for resultado in resultados:
            mes_ano = resultado["mes"].strftime("%m/%Y")
            grupo_id = resultado["grupo_id"]

            grupo_dict = next(
                (
                    g
                    for g in resultado_final
                    if g["mes"] == mes_ano
                    and g["assignment_group_id"] == grupo_id
                ),
                None,
            )

            if not grupo_dict:
                # Buscar a meta do grupo
                try:
                    premissa = Premissas.objects.get(assignment_id=grupo_id)
                    meta_grupo = premissa.meta_mensal
                except Premissas.DoesNotExist:
                    meta_grupo = None

                grupo_dict = {
                    "assignment_group_id": grupo_id,
                    "assignment_group_nome": grupo_map.get(
                        grupo_id, "Desconhecido"
                    ),
                    "mes": mes_ano,
                    "meta_mensal": meta_grupo,
                    "total_tickets": tickets_map.get(
                        f"{mes_ano}_{grupo_id}", 0
                    ),
                    "tecnicos": [],
                }
                resultado_final.append(grupo_dict)

            tecnico = next(
                (
                    t
                    for t in grupo_dict["tecnicos"]
                    if t["tecnico_id"] == resultado["tecnico_id"]
                ),
                None,
            )

            if not tecnico:
                tecnico = {
                    "tecnico_id": resultado["tecnico_id"],
                    "tecnico_nome": tecnico_map.get(
                        resultado["tecnico_id"], "Desconhecido"
                    ),
                    "nota_media": 0,
                    "nota_total": 0,
                    "total_avaliacoes": resultado["total_avaliacoes"],
                    "melhor_criterio": None,
                    "pior_criterio": None,
                    "criterios": [],
                }
                grupo_dict["tecnicos"].append(tecnico)

            criterio = {
                "criterio_id": resultado["criterio__id"],
                "criterio_nome": resultado["criterio__nome"],
                "nota_total": float(resultado["nota_total"]),
                "total_avaliacoes": resultado["total_avaliacoes"],
            }
            criterio["nota_media"] = (
                criterio["nota_total"] / criterio["total_avaliacoes"]
                if criterio["total_avaliacoes"] > 0
                else 0
            )
            tecnico["criterios"].append(criterio)

            tecnico["nota_total"] = sum(
                c["nota_total"] for c in tecnico["criterios"]
            )
            tecnico["nota_media"] = (
                tecnico["nota_total"] / tecnico["total_avaliacoes"]
                if tecnico["total_avaliacoes"] > 0
                else 0
            )

            if tecnico["criterios"]:
                melhor_criterio = max(
                    tecnico["criterios"], key=lambda x: x["nota_media"]
                )
                pior_criterio = min(
                    tecnico["criterios"], key=lambda x: x["nota_media"]
                )
                tecnico["melhor_criterio"] = {
                    "criterio_id": melhor_criterio["criterio_id"],
                    "criterio_nome": melhor_criterio["criterio_nome"],
                    "nota_media": melhor_criterio["nota_media"],
                }
                tecnico["pior_criterio"] = {
                    "criterio_id": pior_criterio["criterio_id"],
                    "criterio_nome": pior_criterio["criterio_nome"],
                    "nota_media": pior_criterio["nota_media"],
                }

            # Atualizar total de tickets do grupo
            grupo_dict["total_tickets"] = sum(
                t["total_avaliacoes"] for t in grupo_dict["tecnicos"]
            )

        return resultado_final
