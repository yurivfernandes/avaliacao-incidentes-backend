from itertools import chain

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
        notas_booleanas = NotaCriterioBooleano.objects.filter(
            avaliacao=avaliacao
        )
        notas_conversao = NotaCriterioConversao.objects.filter(
            avaliacao=avaliacao
        )
        notas = chain(notas_booleanas, notas_conversao)

        serializer = self.get_serializer(notas, many=True)
        return Response(serializer.data)
