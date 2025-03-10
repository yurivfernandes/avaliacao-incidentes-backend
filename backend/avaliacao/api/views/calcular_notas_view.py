from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from ...tasks import LoadCalcularNotas


class CalcularNotasView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        data_referencia = request.data.get("data_referencia")
        avaliacao_id = request.data.get("avaliacao")

        if not data_referencia:
            return Response(
                {"error": "data_referencia é obrigatória"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            with LoadCalcularNotas(
                avaliacao_id=avaliacao_id, data_referencia=data_referencia
            ) as task:
                log = task.run()

            return Response(
                {
                    "message": "Cálculo de notas concluído com sucesso",
                    "log": log,
                }
            )
        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
