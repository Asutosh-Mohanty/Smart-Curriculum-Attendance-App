
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    roll_number = models.CharField(max_length=20, unique=True)
    attendance_percentage = models.FloatField(default=0.0)
    interests = models.TextField(blank=True, help_text="Comma-separated interests for AI recommendations")
    branch = models.ForeignKey('admins.Branch', on_delete=models.SET_NULL, null=True, blank=True)
    degree = models.ForeignKey('admins.Degree', on_delete=models.SET_NULL, null=True, blank=True)
    group = models.ForeignKey('admins.Group', on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.get_full_name()} ({self.roll_number})"