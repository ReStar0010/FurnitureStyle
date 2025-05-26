import os
import tempfile
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework.authentication import SessionAuthentication
from drf_yasg.utils import swagger_auto_schema

from .models import SearchHistory
from .serializers import PictureUploadSerializer, FurnitureTextSerializer, SearchHistorySerializer
from .classifier import classify_furniture_from_image, classify_furniture_from_text
from .search import search_furniture_by_text
from .search import google_image_search


class FurnitureImageView(APIView):
    authentication_classes = [SessionAuthentication]
    permission_classes  = [permissions.IsAuthenticated]

    @swagger_auto_schema(request_body=PictureUploadSerializer)
    def post(self, request):
        """
        POST { "image": <file>, "color": "original" }
        """
        # NOTE - get uploaded file a
        ser = PictureUploadSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        upload = ser.validated_data['image']  # InMemoryUploadedFile
        # NOTE - get color mode
        color_mode = ser.validated_data['color']
        # NOTE - save as tmp file
        ext = os.path.splitext(upload.name)[1] or '.jpg'
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=ext)
        for chunk in upload.chunks():
            tmp.write(chunk)
        tmp.close()

        try:
            # NOTE - send the image to LLM, and return formated result
            formated_query = classify_furniture_from_image(tmp.name, color_mode=color_mode)
        finally:
            # NOTE - remove the tmp file
            try:
                os.remove(tmp.name)
            except OSError:
                pass

        # NOTE - resposonse the result to frontend
        try:
            # NOTE - search history
            SearchHistory.objects.create(
                user=request.user,
                query_type='image',
                color_mode=color_mode,
                furniture_type=formated_query['type'],
                furniture_style=formated_query['style']
            )
            # NOTE - search the funiture with the LLM result(from image)
            shopping_results = search_furniture_by_text(formated_query)
            return Response(
            {
                'type': formated_query['type'],
                'style': formated_query['style'],
                'shopping': shopping_results
            },
            status=status.HTTP_200_OK
        )
        except Exception as e:
            return Response(
                {'error': 'Failed to search furniture'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    

class FurnitureTextAPIView(APIView):
    authentication_classes = [SessionAuthentication]
    permission_classes  = [permissions.IsAuthenticated]
    @swagger_auto_schema(request_body=FurnitureTextSerializer)
    def post(self, request):
        """
        POST { "query": "modern sofa" }
        """
        # NOTE - get the text query
        serializer = FurnitureTextSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        query = serializer.validated_data['query']
        # NOTE - get the color mode
        color_mode = serializer.validated_data['color']
        # NOTE - send query to LLM, and return formated result
        formated_query = classify_furniture_from_text(query, color_mode=color_mode) # formated_query = {type: "sofa", style: "modern"}
        # NOTE - search the furniture with the LLM result
        shopping_results = search_furniture_by_text(formated_query)
        # NOTE - save the search history
        SearchHistory.objects.create(
            user=request.user,
            query_type='text',
            original_query=query,
            color_mode=color_mode,
            furniture_type=formated_query['type'],
            furniture_style=formated_query['style']
        )
        
        return Response(
            {
                "type": formated_query['type'],
                'style': formated_query['style'],
                "shopping": shopping_results 
            },
            status=status.HTTP_200_OK
        )
    
# ...existing code...

class SearchHistoryAPIView(APIView):
    authentication_classes = [SessionAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    
    @swagger_auto_schema(responses={200: SearchHistorySerializer(many=True)})
    def get(self, request):
        """
        Retrieve the search history for the authenticated user
        """
        # Get last 20 searches by default
        limit = request.query_params.get('limit', 20)
        try:
            limit = int(limit)
        except (ValueError, TypeError):
            limit = 20
            
        searches = SearchHistory.objects.filter(user=request.user)[:limit]
        serializer = SearchHistorySerializer(searches, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
        

