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
    

class FavoriteItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='furniture_favorites')
    
    # Item details from search results
    title = models.CharField(max_length=255)
    link = models.URLField(max_length=500)  # Using longer URL field for complex URLs
    price = models.CharField(max_length=50)  # Keep as string to preserve formatting like '$6,854.00'
    image_url = models.URLField(max_length=500)
    position = models.IntegerField(null=True, blank=True)  # Optional, can be used for ordering
    
    # Store the furniture type and style for categorization
    furniture_type = models.CharField(max_length=100)
    furniture_style = models.CharField(max_length=100)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        # Ensure users can't favorite the same item twice
        unique_together = ['user', 'link']
        verbose_name = "Favorite Item"
        verbose_name_plural = "Favorite Items"

    def __str__(self):
        return f"{self.user.username} - {self.title[:30]}"