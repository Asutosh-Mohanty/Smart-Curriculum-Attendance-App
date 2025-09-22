from django.urls import path
from . import views

app_name = "ai_suggestions"

urlpatterns = [
    path("free-suggestions/", views.free_period_suggestions, name="free_suggestions"),
    path("random-suggestions/", views.generate_random_suggestions, name="random_suggestions"),
    path("mark-completed/", views.mark_task_completed, name="mark_completed"),
    path("completed-tasks/", views.get_completed_tasks, name="completed_tasks"),
]
