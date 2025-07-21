from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db import connection


class HealthCheckView(APIView):
    """
    API endpoint that checks the health of the application.
    """
    permission_classes = []
    
    def get(self, request, format=None):
        # Check database connection
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                db_status = "ok"
        except Exception as e:
            db_status = f"error: {str(e)}"
        
        data = {
            "status": "ok",
            "database": db_status,
            "version": "1.0.0",
        }
        return Response(data, status=status.HTTP_200_OK)