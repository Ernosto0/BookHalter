from django.contrib import admin 

# Register your models here.

from .models import Project, Comment, Tag, Books

admin.site.register(Project)
admin.site.register(Comment)
admin.site.register(Tag)
admin.site.register(Books)