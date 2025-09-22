from django.contrib import admin
from .models import Suggestion, CompletedTask

# Register your models here.

@admin.register(Suggestion)
class SuggestionAdmin(admin.ModelAdmin):
    list_display = ("id", "student", "created_at", "source")
    readonly_fields = ("payload",)

@admin.register(CompletedTask)
class CompletedTaskAdmin(admin.ModelAdmin):
    list_display = ("student", "task_title", "time_minutes", "completed_at")
    list_filter = ("completed_at", "student")
    search_fields = ("task_title", "student__user__username")
