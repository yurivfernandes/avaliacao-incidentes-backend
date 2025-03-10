from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from ...models import Criterios, Premissas
from ..serializers import CriterioSerializer


class CriteriosPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 100


class CriteriosView(APIView):
    permission_classes = [IsAuthenticated]
    pagination_class = CriteriosPagination

    def get(self, request, *args, **kwargs):
        premissa_id = request.query_params.get("premissa")
        if not premissa_id:
            return Response(
                {"detail": "Parâmetro 'premissa' é obrigatório"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        criterios = Criterios.objects.filter(premissa_id=premissa_id)

        paginator = self.pagination_class()
        page = paginator.paginate_queryset(criterios, request)
        serializer = CriterioSerializer(page, many=True)

        return Response(
            {
                "count": paginator.page.paginator.count,
                "num_pages": paginator.page.paginator.num_pages,
                "next": paginator.get_next_link(),
                "previous": paginator.get_previous_link(),
                "results": serializer.data,
            }
        )

    def post(self, request, *args, **kwargs):
        premissa_id = request.query_params.get("premissa")
        if not premissa_id:
            return Response(
                {"detail": "Parâmetro 'premissa' é obrigatório"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            premissa = Premissas.objects.get(id=premissa_id)
        except Premissas.DoesNotExist:
            return Response(
                {"detail": "Premissa não encontrada."},
                status=status.HTTP_404_NOT_FOUND,
            )

        data = request.data.copy()
        data["premissa"] = premissa_id

        serializer = CriterioSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk=None, *args, **kwargs):
        premissa_id = request.query_params.get("premissa")
        if not premissa_id:
            return Response(
                {"detail": "Parâmetro 'premissa' é obrigatório"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            criterio = Criterios.objects.get(pk=pk, premissa_id=premissa_id)
        except Criterios.DoesNotExist:
            return Response(
                {"detail": "Critério não encontrado."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = CriterioSerializer(
            criterio, data=request.data, partial=True
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
