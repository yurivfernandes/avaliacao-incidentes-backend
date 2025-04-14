from django.db import models
from rest_framework import filters, generics
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated

from ...models import Empresa
from ..serializers import EmpresaSerializer


class EmpresaListView(generics.ListAPIView):
    queryset = Empresa.objects.all().order_by("nome")
    serializer_class = EmpresaSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = PageNumberPagination
    filter_backends = [filters.SearchFilter]
    search_fields = ["nome", "cnpj"]

    def get_queryset(self):
        queryset = super().get_queryset()
        search = self.request.query_params.get("search", "")

        if search:
            return queryset.filter(
                models.Q(nome__icontains=search)
                | models.Q(cnpj__icontains=search)
            )
        return queryset
