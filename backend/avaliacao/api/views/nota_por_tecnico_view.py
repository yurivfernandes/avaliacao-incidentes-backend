from datetime import datetime, timedelta

from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied
from django.db.models import Avg, Count, F, Sum
from django.db.models.functions import TruncMonth
from dw_analytics.models import AssignmentGroup
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

        # Converter e validar datas
        try:
            start_date = datetime.strptime(start_date, "%Y-%m-%d")
            end_date = datetime.strptime(end_date, "%Y-%m-%d")
        except ValueError:
            raise ValidationError(
                {"error": "Formato de data inválido. Use YYYY-MM-DD"}
            )

        # Base query
        queryset = ResultadoAvaliacao.objects.select_related(
            "avaliacao__incident", "criterio"
        ).filter(
            data_referencia__range=[start_date, end_date],
            avaliacao__incident__assignment_group=assignment_group,
        )

        # Filtros de permissão
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

        # Agrupar resultados
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
                nota_media=Avg("nota"),
                nota_total=Sum("nota"),
                total_avaliacoes=Count("avaliacao", distinct=True),
            )
            .order_by("mes", "grupo_id", "tecnico_id", "criterio__id")
        )

        # Buscar dados dos grupos
        grupos = AssignmentGroup.objects.all()
        grupo_map = {str(g.id): g.dv_assignment_group for g in grupos}

        # Buscar dados dos usuários
        User = get_user_model()
        tecnicos = User.objects.filter(
            id__in=set(r["tecnico_id"] for r in resultados if r["tecnico_id"])
        )
        tecnico_map = {
            str(t.id): f"{t.first_name} {t.last_name}".strip() or t.username
            for t in tecnicos
        }

        # Organizar resultado por grupo e mês
        resultado_final = []

        # Inicializar estruturas de estatísticas
        for resultado in resultados:
            mes_ano = resultado["mes"].strftime("%m/%Y")
            grupo_id = resultado["grupo_id"]

            grupo_mes_key = f"{mes_ano}_{grupo_id}"
            if mes_ano not in grupo_mes_key:
                grupo_mes_key[mes_ano] = []

            if grupo_mes_key not in grupo_mes_key:
                grupo_mes_key[grupo_mes_key] = {
                    "nota_total": 0,
                    "total_avaliacoes": 0,
                    "nota_media": 0,
                }

        for resultado in resultados:
            mes_ano = resultado["mes"].strftime("%m/%Y")
            grupo_id = resultado["grupo_id"]

            # Encontrar ou criar grupo no resultado
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
                grupo_dict = {
                    "assignment_group_id": grupo_id,
                    "assignment_group_nome": grupo_map.get(
                        grupo_id, "Desconhecido"
                    ),
                    "mes": mes_ano,
                    "nota_total": 0,
                    "total_avaliacoes": 0,
                    "nota_media": 0,
                    "total_tickets": 0,  # Novo campo
                    "tecnicos": [],
                }
                resultado_final.append(grupo_dict)

            # Encontrar ou criar técnico no grupo
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
                    "posicao_ranking": 0,
                    "melhor_criterio": None,
                    "pior_criterio": None,
                    "criterios": [],
                }
                grupo_dict["tecnicos"].append(tecnico)

            # Adicionar critério
            criterio = {
                "criterio_id": resultado["criterio__id"],
                "criterio_nome": resultado["criterio__nome"],
                "nota_media": float(resultado["nota_media"]),
                "nota_total": float(resultado["nota_total"]),
                "total_avaliacoes": resultado["total_avaliacoes"],
            }
            tecnico["criterios"].append(criterio)

            # Calcular médias e totais do técnico
            tecnico["nota_total"] = sum(
                c["nota_total"] for c in tecnico["criterios"]
            )
            tecnico["nota_media"] = (
                tecnico["nota_total"] / tecnico["total_avaliacoes"]
                if tecnico["total_avaliacoes"] > 0
                else 0
            )

            # Identificar melhor e pior critério
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

            # Atualizar totais do grupo após processar cada técnico
            grupo_dict["nota_total"] = sum(
                t["nota_total"] for t in grupo_dict["tecnicos"]
            )
            grupo_dict["total_avaliacoes"] = sum(
                t["total_avaliacoes"] for t in grupo_dict["tecnicos"]
            )
            grupo_dict["total_tickets"] = sum(  # Novo cálculo
                t["total_avaliacoes"] for t in grupo_dict["tecnicos"]
            )

            # Calcular a média do grupo como a média das médias dos técnicos
            tecnicos_com_avaliacoes = [
                t for t in grupo_dict["tecnicos"] if t["total_avaliacoes"] > 0
            ]
            if tecnicos_com_avaliacoes:
                grupo_dict["nota_media"] = sum(
                    t["nota_media"] for t in tecnicos_com_avaliacoes
                ) / len(tecnicos_com_avaliacoes)
            else:
                grupo_dict["nota_media"] = 0

        # Remover todo o código de estatísticas_por_mes e estatisticas_por_grupo_mes
        return resultado_final
