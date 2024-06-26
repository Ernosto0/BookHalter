from django.db import models
from django.conf import settings
from django.contrib.auth.models import User

import uuid


# Create your models here.




class Tag(models.Model):
    name = models.CharField(max_length=200)
    created = models.DateTimeField(auto_now_add=True)
    id = models.UUIDField(default=uuid.uuid4, unique=True, primary_key=True, editable=False)

    def __str__(self):
        return self.name

class Books(models.Model):
    name = models.CharField(max_length=200)
    author = models.CharField(max_length=100, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    tags = models.ManyToManyField('tag', blank=True)
    created = models.DateTimeField(auto_now_add=True)
    id = models.UUIDField(default=uuid.uuid4, unique=True, primary_key=True, editable=False)
    vote_total = models.IntegerField(default=0, null=True, blank=True)
    vote_ratio = models.IntegerField(default=0, null=True, blank=True) 
    upvotes_count = models.IntegerField(default=0, null=True, blank=True)
    featured_image = models.ImageField(null=True, blank=True, default='book.png')
    cover_image_url = models.URLField(max_length=250, null=True, blank=True)
    published_year = models.IntegerField(null=True, blank=True)
    amazon_id = models.IntegerField(default=0, null=True, blank=True)
    googlebooks_link = models.URLField(max_length=250, null=True, blank=True)
    categories = models.CharField(max_length=150, null=True, blank=True)
    recommended_count = models.IntegerField(default=0, null=True, blank=True)   

    class Meta:
        unique_together = ('name', 'author')

    def __str__(self):
        return self.name

class Comment(models.Model):
    VOTE_TYPE = (
        ('up', 'Up Vote'),
        ('down', 'Down Vote'),
    )
    # anonymous users for easier tests 
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)

    book = models.ForeignKey(Books, on_delete=models.CASCADE)
    body = models.TextField(null=True, blank=True)
    comment_text = models.CharField(max_length=200, choices=VOTE_TYPE)
    created = models.DateTimeField(auto_now_add=True)
    id = models.UUIDField(default=uuid.uuid4, unique=True, primary_key=True, editable=False)
    
    def __str__(self):
        return f'Comment by a user'

class Vote(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    book = models.ForeignKey(Books, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    vote_type = models.CharField(max_length=4, choices=(('up', 'Upvote'), ('down', 'Downvote')))
