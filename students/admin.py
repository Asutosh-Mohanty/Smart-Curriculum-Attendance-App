from django.contrib import admin
from .models import Student


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('user', 'roll_number', 'attendance_percentage', 'created_at')
    list_filter = ('created_at', 'attendance_percentage')
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'roll_number')
    readonly_fields = ('created_at',)