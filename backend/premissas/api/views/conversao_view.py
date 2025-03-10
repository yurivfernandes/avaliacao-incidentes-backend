from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from ...models import Conversao, Criterios
from ..serializers import ConversaoSerializer


class ConversaoView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        criterio = get_object_or_404(
            Criterios, pk=request.query_params.get("criterio")
        )
        conversoes = Conversao.objects.filter(criterio=criterio)
        serializer = ConversaoSerializer(conversoes, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = ConversaoSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk=None):
        conversao = get_object_or_404(Conversao, pk=pk)

        serializer = ConversaoSerializer(
            conversao, data=request.data, partial=True
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
