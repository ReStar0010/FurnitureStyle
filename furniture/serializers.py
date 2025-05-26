from rest_framework import serializers
from furniture.models import SearchHistory

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

