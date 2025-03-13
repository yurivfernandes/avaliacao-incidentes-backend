from itertools import chain

from django.db.models import Avg, Max, Min
from django.db.models.functions import TruncMonth
from django.shortcuts import get_object_or_404
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from ...models import Avaliacao, NotaCriterioBooleano, NotaCriterioConversao
from ..serializers import NotaAvaliacaoSerializer


class NotasAvaliacaoView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = NotaAvaliacaoSerializer

    def get(self, request, *args, **kwargs):
        avaliacao = get_object_or_404(
            Avaliacao, id=self.request.query_params.get("avaliacao")
        )

        # Obter todas as notas
        notas_booleanas = NotaCriterioBooleano.objects.filter(avaliacao=avaliacao)
        notas_conversao = NotaCriterioConversao.objects.filter(avaliacao=avaliacao)
        
        # Calcular pontos fortes e fracos
        todas_notas = chain(notas_booleanas, notas_conversao)
        notas_por_criterio = {}
        for nota in todas_notas:
            criterio_nome = nota.criterio.nome
            valor_nota = nota.valor if hasattr(nota, 'valor') else (1 if nota.resposta else 0)
            notas_por_criterio[criterio_nome] = valor_nota

        ponto_forte = max(notas_por_criterio.items(), key=lambda x: x[1])
        ponto_fraco = min(notas_por_criterio.items(), key=lambda x: x[1])

        # Calcular ranking mensal
        mes_referencia = avaliacao.data_referencia.replace(day=1)
        avaliacoes_mes = Avaliacao.objects.filter(
            data_referencia__year=mes_referencia.year,
            data_referencia__month=mes_referencia.month
        ).annotate(nota_media=Avg('notas_booleanas__valor') + Avg('notas_conversao__valor'))
        
        ranking = list(avaliacoes_mes.order_by('-nota_media'))
        posicao_ranking = ranking.index(avaliacao) + 1

        # Preparar resposta
        serializer = self.get_serializer(chain(notas_booleanas, notas_conversao), many=True)
        response_data = {
            'notas': serializer.data,
            'posicao_ranking': posicao_ranking,
            'total_tecnicos_mes': len(ranking),
            'ponto_forte': {
                'criterio': ponto_forte[0],
                'nota': ponto_forte[1]
            },
            'ponto_melhoria': {
                'criterio': ponto_fraco[0],
                'nota': ponto_fraco[1]
            },
            'mes_referencia': mes_referencia.strftime('%Y-%m')
        }

        return Response(response_data)
