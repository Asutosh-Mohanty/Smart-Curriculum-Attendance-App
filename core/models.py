from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Attendance(models.Model):
    student = models.ForeignKey('students.Student', on_delete=models.CASCADE)
    subject = models.ForeignKey('teachers.Subject', on_delete=models.CASCADE)
    date = models.DateField(default=timezone.now)
    is_present = models.BooleanField(default=False)
    marked_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['student', 'subject', 'date']
    
    def __str__(self):
        status = "Present" if self.is_present else "Absent"
        return f"{self.student.user.get_full_name()} - {self.subject.name} - {self.date} ({status})"


class Material(models.Model):
    title = models.CharField(max_length=200)
    file = models.FileField(upload_to='materials/')
    subject = models.ForeignKey('teachers.Subject', on_delete=models.CASCADE)
    uploaded_by = models.ForeignKey('teachers.Teacher', on_delete=models.CASCADE)
    upload_date = models.DateTimeField(auto_now_add=True)
    description = models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.title} - {self.subject.name}"


class Announcement(models.Model):
    TARGET_CHOICES = [
        ('all', 'All Users'),
        ('students', 'Students Only'),
        ('teachers', 'Teachers Only'),
    ]
    
    title = models.CharField(max_length=200)
    content = models.TextField()
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    target_audience = models.CharField(max_length=20, choices=TARGET_CHOICES, default='all')
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} ({self.get_target_audience_display()})"