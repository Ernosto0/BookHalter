from django.contrib.auth.models import User
from django.db import models
from projects.models import Books



class UserBookData(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='book_data')
    favorite_books = models.ManyToManyField(Books, related_name='favorited_by', blank=True, help_text="User's favorite books")
    read_books = models.ManyToManyField(Books, related_name='read_by', blank=True, help_text="User's read books")
    user_reading_persona = models.TextField(blank=True, help_text="User's reading persona")
    vote_count = models.IntegerField(default=0, null=True, blank=True, help_text="Count user's votes, reset every 20 books.")
    last_recommendation_time = models.DateTimeField(default=None, null=True, blank=True)
    
    def __str__(self):
        return f"{self.user.username}'s book data"

