from rest_framework import serializers
from .models import Task, TaskLog


class TaskLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskLog
        fields = ['id', 'message', 'level', 'created_at']
        read_only_fields = ['id', 'created_at']


class TaskSerializer(serializers.ModelSerializer):
    logs = TaskLogSerializer(many=True, read_only=True, required=False)
    user_username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = Task
        fields = [
            'id', 'title', 'task_type', 'status', 'progress', 'result',
            'error_message', 'celery_task_id', 'parameters', 'max_retries',
            'retry_count', 'scheduled_at', 'created_at', 'started_at',
            'completed_at', 'logs', 'user_username'
        ]
        read_only_fields = [
            'id', 'status', 'progress', 'result', 'error_message',
            'celery_task_id', 'retry_count', 'created_at', 'started_at',
            'completed_at', 'logs', 'user_username'
        ]


class TaskCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ['title', 'task_type', 'parameters', 'max_retries', 'scheduled_at']
        extra_kwargs = {
            'scheduled_at': {'required': False},
            'parameters': {'required': False},
        }

