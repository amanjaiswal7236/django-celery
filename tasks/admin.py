from django.contrib import admin
from .models import Task, TaskLog


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'task_type', 'status', 'progress', 'created_at', 'completed_at']
    list_filter = ['status', 'task_type', 'created_at']
    search_fields = ['title', 'user__username']
    readonly_fields = ['celery_task_id', 'created_at', 'started_at', 'completed_at']
    date_hierarchy = 'created_at'


@admin.register(TaskLog)
class TaskLogAdmin(admin.ModelAdmin):
    list_display = ['task', 'level', 'message', 'created_at']
    list_filter = ['level', 'created_at']
    search_fields = ['task__title', 'message']
    readonly_fields = ['created_at']
    date_hierarchy = 'created_at'

