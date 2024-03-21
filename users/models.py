from django.contrib.auth.models import User
from django.db import models

class UserBookData(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='book_data')
    favorite_books = models.TextField(blank=True, help_text="List of user's favorite books")
    user_reading_persona = models.TextField(blank=True, help_text="User's reading persona")
    
    def __str__(self):
        return f"{self.user.username}'s book data"

