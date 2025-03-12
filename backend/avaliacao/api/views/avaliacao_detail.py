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

        user = self.request.user
        if user.is_staff:
            return queryset
        elif user.is_gestor and user.assignment_groups.exists():
            return queryset.filter(
                incident__assignment_group__in=user.assignment_groups.all()
            )
        return queryset.filter(incident__resolved_by=user.id)
