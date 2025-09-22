from django.contrib import admin
from .models import Teacher, Subject, Timetable, QRCode


@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ('user', 'employee_id', 'department', 'created_at')
    list_filter = ('department', 'created_at')
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'employee_id')
    readonly_fields = ('created_at',)


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'teacher')
    list_filter = ('teacher__department',)
    search_fields = ('name', 'code', 'teacher__user__username')


@admin.register(Timetable)
class TimetableAdmin(admin.ModelAdmin):
    list_display = ('day', 'time_slot', 'subject', 'room_number')
    list_filter = ('day', 'subject')
    search_fields = ('subject__name', 'room_number')


@admin.register(QRCode)
class QRCodeAdmin(admin.ModelAdmin):
    list_display = ('subject', 'teacher', 'created_at', 'expires_at', 'is_active')
    list_filter = ('is_active', 'created_at', 'expires_at')
    search_fields = ('subject__name', 'teacher__user__username')
    readonly_fields = ('created_at', 'qr_data')