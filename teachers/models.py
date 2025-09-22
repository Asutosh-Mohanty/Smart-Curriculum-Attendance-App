from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Teacher(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    employee_id = models.CharField(max_length=20, unique=True)
    department = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.get_full_name()} ({self.employee_id})"


class Subject(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=10, unique=True)
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name='subjects')
    
    def __str__(self):
        return f"{self.name} ({self.code})"


class Timetable(models.Model):
    DAY_CHOICES = [
        ('Monday', 'Monday'),
        ('Tuesday', 'Tuesday'),
        ('Wednesday', 'Wednesday'),
        ('Thursday', 'Thursday'),
        ('Friday', 'Friday'),
        ('Saturday', 'Saturday'),
    ]
    
    TIME_CHOICES = [
        ('09:00', '09:00 AM'),
        ('10:00', '10:00 AM'),
        ('11:00', '11:00 AM'),
        ('12:00', '12:00 PM'),
        ('13:00', '01:00 PM'),
        ('14:00', '02:00 PM'),
        ('15:00', '03:00 PM'),
        ('16:00', '04:00 PM'),
    ]
    
    day = models.CharField(max_length=10, choices=DAY_CHOICES)
    time_slot = models.CharField(max_length=5, choices=TIME_CHOICES)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    room_number = models.CharField(max_length=20)
    
    class Meta:
        unique_together = ['day', 'time_slot']
    
    def __str__(self):
        return f"{self.day} {self.time_slot} - {self.subject.name}"


class QRCode(models.Model):
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    qr_data = models.TextField()  # Store the QR code data
    
    def __str__(self):
        return f"QR Code for {self.subject.name} - {self.teacher.user.get_full_name()}"