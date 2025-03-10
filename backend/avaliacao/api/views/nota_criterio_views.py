from django.shortcuts import get_object_or_404
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from ...models import Avaliacao, NotaCriterioBooleano, NotaCriterioConversao
from ..serializers import (
    NotaCriterioBooleanoSerializer,
    NotaCriterioConversaoSerializer,
)


class NotaCriterioBooleanoListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = NotaCriterioBooleanoSerializer

    def get_queryset(self):
        avaliacao = get_object_or_404(
            Avaliacao, id=self.request.query_params.get("avaliacao")
        )
        return NotaCriterioBooleano.objects.filter(avaliacao=avaliacao)

    def perform_create(self, serializer):
        avaliacao = get_object_or_404(
            Avaliacao, id=self.request.query_params.get("avaliacao")
        )
        serializer.save(avaliacao=avaliacao)


class NotaCriterioConversaoListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = NotaCriterioConversaoSerializer

    def get_queryset(self):
        avaliacao = get_object_or_404(
            Avaliacao, id=self.request.query_params.get("avaliacao")
        )
        return NotaCriterioConversao.objects.filter(avaliacao=avaliacao)

    def perform_create(self, serializer):
        avaliacao = get_object_or_404(
            Avaliacao, id=self.request.query_params.get("avaliacao")
        )
        serializer.save(avaliacao=avaliacao)
