from django.db import models
from django.contrib.auth.models import User

class SearchHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='furniture_searches')
    query_type = models.CharField(max_length=10, choices=[('text', 'Text'), ('image', 'Image')])
    original_query = models.TextField(blank=True, null=True)  # For text queries
    color_mode = models.CharField(max_length=20, default='original')
    furniture_type = models.CharField(max_length=100)
    furniture_style = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Search histories'

    def __str__(self):
        return f"{self.user.username} - {self.furniture_type} ({self.furniture_style})"