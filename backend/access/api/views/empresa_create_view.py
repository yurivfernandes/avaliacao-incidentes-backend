from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from ..serializers import EmpresaCreateSerializer


class EmpresaCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if not request.user.is_staff:
            return Response(
                {"error": "Apenas usuários staff podem criar empresas"},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = EmpresaCreateSerializer(data=request.data)

        if serializer.is_valid():
            try:
                empresa = serializer.save()
                return Response(
                    {
                        "message": "Empresa criada com sucesso",
                        "id": empresa.id,
                        "nome": empresa.nome,
                    },
                    status=status.HTTP_201_CREATED,
                )
            except Exception as e:
                return Response(
                    {"error": f"Erro ao criar empresa: {str(e)}"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
