from django.urls import path
from .views import *

urlpatterns = [
    path('image/', FurnitureImageView.as_view(), name='furniture-image'),
    path('text/', FurnitureTextAPIView.as_view(), name='furniture-text'),
    path('search-history/', SearchHistoryAPIView.as_view(), name='search-history'),
    path('favorites/', FavoritesAPIView.as_view(), name='favorites'),
    path('favorites/<int:pk>/', FavoriteDetailAPIView.as_view(), name='favorite-detail'),
]

