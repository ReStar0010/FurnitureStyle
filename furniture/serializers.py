from rest_framework import serializers
from furniture.models import SearchHistory, FavoriteItem

COLOR_CHOICES = [
    ('original',      '原本'),
    ('complementary', '互補色'),
    ('monochrome',    '單色'),
    ('analogous',     '類似色'),
]

class PictureUploadSerializer(serializers.Serializer):
    image = serializers.ImageField(
        use_url=False,
        help_text="上傳一張圖片"
    )
    color = serializers.ChoiceField(
        choices=COLOR_CHOICES,
        default='original',
        help_text="選擇顏色模式"
    )

class FurnitureTextSerializer(serializers.Serializer):
    query = serializers.CharField()
    color = serializers.ChoiceField(
            choices=COLOR_CHOICES,
            default='original',
            help_text="選擇顏色模式"
        ) 
# ...existing code...

class SearchHistorySerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = SearchHistory
        fields = ['id', 'username', 'query_type', 'original_query', 'color_mode', 
                  'furniture_type', 'furniture_style', 'created_at']
        read_only_fields = ['id', 'username', 'created_at']

class FavoriteItemSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = FavoriteItem
        fields = [
            'id', 'username', 'title', 'link', 'price', 'image_url', 
            'position', 'furniture_type', 'furniture_style', 'created_at'
        ]
        read_only_fields = ['id', 'username', 'created_at']

class AddToFavoriteSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=255)
    link = serializers.URLField(max_length=500)
    price = serializers.CharField(max_length=50)
    image_url = serializers.CharField(max_length=500)
    position = serializers.IntegerField(required=False)
    furniture_type = serializers.CharField(max_length=100)
    furniture_style = serializers.CharField(max_length=100)