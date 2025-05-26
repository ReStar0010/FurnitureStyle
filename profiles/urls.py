from django.urls import path
from .views import *

urlpatterns = [
   path('', ProfileAPIView.as_view(), name='user-profile'),
]
