from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework.authentication import SessionAuthentication
from drf_yasg.utils import swagger_auto_schema

from .models import UserProfile
from .serializers import UserProfileSerializer

class ProfileAPIView(APIView):
    authentication_classes = [SessionAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    
    @swagger_auto_schema(responses={200: UserProfileSerializer()})
    def get(self, request):
        """
        Get the current user's profile
        """
        profile, created = UserProfile.objects.get_or_create(user=request.user)
        serializer = UserProfileSerializer(profile)
        return Response(serializer.data)
    
    @swagger_auto_schema(request_body=UserProfileSerializer)
    def put(self, request):
        """
        Update the current user's profile
        """
        profile, created = UserProfile.objects.get_or_create(user=request.user)
        serializer = UserProfileSerializer(profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)