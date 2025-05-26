from rest_framework import serializers
from .models import UserProfile

class UserProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)
    
    class Meta:
        model = UserProfile
        fields = [
            'id', 
            'username', 
            'email', 
            'full_name', 
            'phone_number',
            'address', 
            'city', 
            'country',
            'preferred_styles', 
            'preferred_colors', 
            'room_types',
            'created_at', 
            'updated_at'
        ]
        read_only_fields = ['id', 'username', 'email', 'created_at', 'updated_at']