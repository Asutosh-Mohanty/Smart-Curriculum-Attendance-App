from django.urls import path
from . import views

app_name = 'teachers'

urlpatterns = [
    path('dashboard/', views.teacher_dashboard, name='dashboard'),
    path('groups/', views.group_selection, name='group_selection'),
    path('group/<int:subject_id>/', views.group_dashboard, name='group_dashboard'),
    path('group/<int:subject_id>/generate-qr/', views.generate_qr, name='generate_qr'),
    path('group/<int:subject_id>/upload-material/', views.upload_material, name='upload_material'),
    path('attendance/<int:assignment_id>/', views.attendance_report, name='attendance_report'),
]


