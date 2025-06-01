from django.urls import path
from . import views

urlpatterns = [
    path('csrf/', views.get_csrf, name='get-csrf'),
    path('login/', views.api_login, name='login'),
    path('logout/', views.api_logout, name='logout'),
    path('auth-status/', views.check_auth_status, name='auth-status'),
    path('register/', views.api_register, name='register'),
    path('user-exist-check/', views.user_exist_check, name='user-exist-check'),
    path('google/', views.google_auth, name='google_auth'),
]