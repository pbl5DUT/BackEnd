from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

class AuthCheckView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """
        Simple endpoint to verify authentication is working.
        """
        return Response({
            'status': 'success',
            'message': 'Authentication successful',
            'user': {
                'id': request.user.id,
                'username': request.user.username,
                'email': request.user.email
            }
        }, status=status.HTTP_200_OK)
