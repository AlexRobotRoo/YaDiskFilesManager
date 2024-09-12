from django.contrib import admin
from django.urls import path
from disk import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('files/', views.show_files, name='list_files'),    
]