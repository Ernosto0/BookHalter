from django.urls import path ,include
from . import views
from django.contrib.auth import views as auth_views



urlpatterns = [
    path('', views.projects, name="projects"),
    path('recommended_books/', views.recommended_books, name='recommended_books'),
    path('book/<uuid:book_id>/', views.book_detail, name='book-detail'),
    path('vote/<uuid:book_id>', views.vote, name='vote'),
    path('post_comment/<uuid:book_id>/', views.post_comment, name='post_comment'),
    path('users/', include('users.urls')),
    path('book/<uuid:book_id>/toggle_read_status/', views.toggle_read_status, name='toggle_read_status'),
    path('get_read_books/', views.get_read_books, name='get_read_books'),
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
]