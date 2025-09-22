from django.contrib import admin
from core.models import Announcement, Material, Attendance
from .models import GroupSubjectAssignment


@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_by', 'created_at', 'is_active')
    list_filter = ('is_active', 'created_at')
    search_fields = ('title', 'content', 'created_by__username')
    readonly_fields = ('created_at',)


@admin.register(Material)
class MaterialAdmin(admin.ModelAdmin):
    list_display = ('title', 'subject', 'uploaded_by', 'upload_date')
    list_filter = ('subject', 'uploaded_by', 'upload_date')
    search_fields = ('title', 'subject__name', 'uploaded_by__user__username')
    readonly_fields = ('upload_date',)


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('student', 'subject', 'date', 'is_present', 'marked_at')
    list_filter = ('date', 'is_present', 'subject')
    search_fields = ('student__user__username', 'subject__name')
    readonly_fields = ('marked_at',)


@admin.register(GroupSubjectAssignment)
class GroupSubjectAssignmentAdmin(admin.ModelAdmin):
    list_display = ('group', 'subject', 'teacher')
    list_filter = ('group__branch', 'group__degree', 'subject', 'teacher')
    search_fields = (
        'group__name', 'group__branch__name', 'group__degree__name',
        'subject__name', 'subject__code', 'teacher__user__first_name', 'teacher__user__last_name'
    )