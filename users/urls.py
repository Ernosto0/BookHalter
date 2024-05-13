from django.urls import path 
from django.contrib.auth.views import LoginView

from . import views
from django.contrib.auth import views as auth_views 

app_name = 'users'

urlpatterns = [
    path('', views.profiles, name="profiles"),
    path('ajax_login/', views.ajax_login, name='ajax_login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'), 
    path('register/', views.register, name='register'),

]