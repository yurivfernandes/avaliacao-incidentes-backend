from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from ..serializers import AvaliacaoCompletaSerializer
from .processadores_criterios import (
    ProcessadorCriterioBooleano,
    ProcessadorCriterioConversao,
)


class CriarAvaliacaoCompletaView(APIView):
    def post(self, request):
        data = request.data.copy()
        criterios_data = data.get("criterios", [])

        serializer = AvaliacaoCompletaSerializer(data=data)

        if serializer.is_valid():
            # Adiciona o usuário atual aos dados antes de salvar
            avaliacao = serializer.save(user=request.user)

            try:
                for criterio in criterios_data:
                    if criterio["tipo"] == "booleano":
                        ProcessadorCriterioBooleano().processar(
                            avaliacao, criterio
                        )
                    elif criterio["tipo"] == "conversao":
                        ProcessadorCriterioConversao().processar(
                            avaliacao, criterio
                        )

                return Response(
                    serializer.data, status=status.HTTP_201_CREATED
                )
            except Exception as e:
                avaliacao.delete()  # Remove a avaliação se houver erro ao processar os critérios
                return Response(
                    {"error": f"Erro ao processar critérios: {str(e)}"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
