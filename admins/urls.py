from django.urls import path
from . import views

app_name = 'admins'

urlpatterns = [
    path('dashboard/', views.admin_dashboard, name='dashboard'),
    path('create-announcement/', views.create_announcement, name='create_announcement'),
    path('add-user/', views.add_user, name='add_user'),
    path('users/', views.users_list, name='users_list'),
    path('users/<int:user_id>/edit/', views.user_edit, name='user_edit'),
    path('users/<int:user_id>/delete/', views.user_delete, name='user_delete'),
    path('branches/', views.branches_list, name='branches_list'),
    path('branches/create/', views.branch_create, name='branch_create'),
    path('branches/<int:pk>/edit/', views.branch_edit, name='branch_edit'),
    path('branches/<int:pk>/delete/', views.branch_delete, name='branch_delete'),
    path('degrees/', views.degrees_list, name='degrees_list'),
    path('degrees/create/', views.degree_create, name='degree_create'),
    path('degrees/<int:pk>/edit/', views.degree_edit, name='degree_edit'),
    path('degrees/<int:pk>/delete/', views.degree_delete, name='degree_delete'),
    path('groups/', views.groups_list, name='groups_list'),
    path('groups/create/', views.group_create, name='group_create'),
    path('groups/<int:pk>/edit/', views.group_edit, name='group_edit'),
    path('groups/<int:pk>/delete/', views.group_delete, name='group_delete'),
    path('subjects/', views.subjects_list, name='subjects_list'),
    path('subjects/create/', views.subject_create, name='subject_create'),
    path('subjects/<int:pk>/edit/', views.subject_edit, name='subject_edit'),
    path('subjects/<int:pk>/delete/', views.subject_delete, name='subject_delete'),
    # Group-Subject assignments
    path('assignments/', views.assignments_list, name='assignments_list'),
    path('assignments/create/', views.assignment_create, name='assignment_create'),
    path('assignments/<int:pk>/delete/', views.assignment_delete, name='assignment_delete'),
    # API
    path('api/groups/', views.api_groups_by_degree_branch, name='api_groups'),
    path('api/branches/', views.api_branches_by_degree, name='api_branches'),
]


