from django.db.models import Q
from rest_framework import generics
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from ...models import Avaliacao
from ..serializers import AvaliacaoSerializer


class CustomPageNumberPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 1000


class AvaliacaoListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPageNumberPagination
    serializer_class = AvaliacaoSerializer

    def get_queryset(self):
        queryset = (
            Avaliacao.objects.select_related(
                "user",
                "incident",
            )
            .prefetch_related(
                "notacriteriobooleano_set__criterio",
                "notacriterioconversao_set__criterio",
                "notacriterioconversao_set__conversao",
            )
            .order_by("-created_at")
            .distinct()
        )

        user = self.request.user

        if user.is_staff:
            pass
        elif user.is_gestor:
            if user.assignment_groups.exists():
                assignment_group_ids = list(
                    map(
                        str,
                        user.assignment_groups.values_list("id", flat=True),
                    )
                )
                queryset = queryset.filter(
                    incident__assignment_group__in=assignment_group_ids
                )
            else:
                return Avaliacao.objects.none()
        else:
            queryset = queryset.filter(incident__resolved_by=user.id)

        search = self.request.query_params.get("search", "")
        if search:
            queryset = queryset.filter(
                Q(incident__number__icontains=search)
                | Q(incident__resolved_by=search if search.isdigit() else None)
            )

        return queryset

    def get_paginated_response(self, data):
        assert self.paginator is not None
        return Response(
            {
                "count": self.paginator.page.paginator.count,
                "num_pages": self.paginator.page.paginator.num_pages,
                "next": self.paginator.get_next_link(),
                "previous": self.paginator.get_previous_link(),
                "results": data,
            }
        )
