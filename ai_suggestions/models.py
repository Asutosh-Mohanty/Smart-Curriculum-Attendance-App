from django.db import models
from django.conf import settings

# Create your models here.

class Suggestion(models.Model):
    # Keep a nullable FK to student if the Student model exists
    # We'll link to students.models.Student using a lazy string to avoid circular imports
    student = models.ForeignKey("students.Student", null=True, blank=True, on_delete=models.SET_NULL)
    payload = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)
    source = models.CharField(max_length=64, default="openai")

    def __str__(self):
        return f"Suggestion {self.id} for {self.student}"


class CompletedTask(models.Model):
    """Track completed AI suggestions for students"""
    student = models.ForeignKey("students.Student", on_delete=models.CASCADE)
    task_title = models.CharField(max_length=200)
    task_reason = models.TextField(blank=True)
    time_minutes = models.IntegerField(default=10)
    completed_at = models.DateTimeField(auto_now_add=True)
    suggestion_id = models.ForeignKey(Suggestion, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        ordering = ['-completed_at']

    def __str__(self):
        return f"{self.student.user.username} completed: {self.task_title}"