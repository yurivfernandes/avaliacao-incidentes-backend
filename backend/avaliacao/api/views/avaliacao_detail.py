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
        elif user.is_gestor:
            if user.assignment_groups.exists():
                assignment_group_ids = list(
                    map(
                        str,
                        user.assignment_groups.values_list("id", flat=True),
                    )
                )
                return queryset.filter(
                    incident__assignment_group__in=assignment_group_ids
                )
            else:
                return Avaliacao.objects.none()
        else:
            return queryset.filter(incident__resolved_by=user.id)
