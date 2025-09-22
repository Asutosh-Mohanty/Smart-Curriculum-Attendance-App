from django.urls import path
from . import views

app_name = 'students'

urlpatterns = [
    path('dashboard/', views.student_dashboard, name='dashboard'),
    path('scan-qr/', views.scan_qr, name='scan_qr'),
    path('materials/', views.materials_list, name='materials_list'),
    path('download/<int:material_id>/', views.download_material, name='download_material'),
]


