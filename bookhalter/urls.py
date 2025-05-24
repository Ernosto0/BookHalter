
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static




urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('projects.urls')),
    path('users/', include(('users.urls', 'users'), namespace='users')),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'), 
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)