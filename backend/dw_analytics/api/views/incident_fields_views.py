from django.db import connection
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView


class IncidentFieldsView(APIView):
    def get(self, request):
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'f_incident' 
                AND column_name NOT IN ('number', 'id')
                ORDER BY column_name;
            """)
            fields = [row[0] for row in cursor.fetchall()]

        return Response({"fields": fields}, status=status.HTTP_200_OK)
