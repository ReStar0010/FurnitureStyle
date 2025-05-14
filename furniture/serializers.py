from rest_framework import serializers

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


