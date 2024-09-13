from django.contrib import admin
from django.urls import path
from disk import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('files/', views.show_files, name='list_files'),
    path('files/download-selected/', views.download_selected_files, name='download_selected_files'),
    path('download/<str:public_key>/<path:path>/', views.download_file, name='download_file'),
]