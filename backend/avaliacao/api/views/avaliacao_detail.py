from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from ...models import Avaliacao
from ..serializers import AvaliacaoSerializer


class AvaliacaoDetailView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = AvaliacaoSerializer
    queryset = Avaliacao.objects.all()

    def get_queryset(self):
        queryset = Avaliacao.objects.select_related(
            "user",
            "incident",
        ).prefetch_related(
            "notacriteriobooleano_set__criterio",
            "notacriterioconversao_set__criterio",
            "notacriterioconversao_set__conversao",
        )
