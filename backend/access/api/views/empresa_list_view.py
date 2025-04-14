from django.db import models
from rest_framework import filters, generics
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated

from ...models import Empresa
from ..serializers import EmpresaSerializer


class EmpresaListView(generics.ListAPIView):
    serializer_class = EmpresaSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = PageNumberPagination
    filter_backends = [filters.SearchFilter]
    search_fields = ["nome", "cnpj"]

    def get_queryset(self):
        if not self.request.user.is_staff:
            # Se não for staff, retorna apenas a empresa do usuário
            return Empresa.objects.filter(
                id=self.request.user.empresa.id
            ).order_by("nome")

        # Se for staff, retorna todas as empresas
        queryset = Empresa.objects.all().order_by("nome")
        search = self.request.query_params.get("search", "")

        if search:
            return queryset.filter(
                models.Q(nome__icontains=search)
                | models.Q(cnpj__icontains=search)
            )
        return queryset
