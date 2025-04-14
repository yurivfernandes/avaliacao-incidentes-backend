from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from ...models import Empresa
from ..serializers import EmpresaSerializer


class EmpresaEditView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, empresa_id):
        try:
            empresa = Empresa.objects.get(id=empresa_id)
            serializer = EmpresaSerializer(empresa)
            return Response(serializer.data)
        except Empresa.DoesNotExist:
            return Response(
                {"error": "Empresa não encontrada"},
                status=status.HTTP_404_NOT_FOUND,
            )

    def patch(self, request, empresa_id):
        if not request.user.is_staff:
            return Response(
                {"error": "Apenas usuários staff podem editar empresas"},
                status=status.HTTP_403_FORBIDDEN,
            )

        try:
            empresa = Empresa.objects.get(id=empresa_id)
            serializer = EmpresaSerializer(
                empresa, data=request.data, partial=True
            )

            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)

            return Response(
                serializer.errors, status=status.HTTP_400_BAD_REQUEST
            )

        except Empresa.DoesNotExist:
            return Response(
                {"error": "Empresa não encontrada"},
                status=status.HTTP_404_NOT_FOUND,
            )
