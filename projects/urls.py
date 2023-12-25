from django.urls import path
from . import views



urlpatterns = [
    path('', views.projects, name="projects"),
    # path('get_result/', views.get_result, name='get_result'),
    path('recommended_books/', views.recommended_books, name='recommended_books'),
    path('book/<uuid:book_id>/', views.book_detail, name='book-detail'),
    path('vote/', views.vote, name='vote'),
    path('post_comment/<uuid:book_id>/', views.post_comment, name='post_comment'),
]