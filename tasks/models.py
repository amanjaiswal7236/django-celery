from django.db import models
from django.conf import settings
from django.utils import timezone

# Use settings.AUTH_USER_MODEL instead of get_user_model() at module level
# This avoids AppRegistryNotReady errors


class Task(models.Model):
    TASK_TYPES = [
        ('file_processing', 'File Processing'),
        ('scraping', 'Web Scraping'),
        ('report_generation', 'Report Generation'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('running', 'Running'),
        ('success', 'Success'),
        ('failed', 'Failed'),
        ('retrying', 'Retrying'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='tasks')
    title = models.CharField(max_length=200)
    task_type = models.CharField(max_length=50, choices=TASK_TYPES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    progress = models.IntegerField(default=0)  # 0-100
    result = models.TextField(blank=True, null=True)
    error_message = models.TextField(blank=True, null=True)
    celery_task_id = models.CharField(max_length=255, blank=True, null=True, unique=True)
    
    # Task parameters (stored as JSON-like text)
    parameters = models.JSONField(default=dict, blank=True)
    
    # Retry settings
    max_retries = models.IntegerField(default=0)
    retry_count = models.IntegerField(default=0)
    
    # Scheduling
    scheduled_at = models.DateTimeField(null=True, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['status']),
            models.Index(fields=['celery_task_id']),
        ]

    def __str__(self):
        return f"{self.title} ({self.status})"

    def mark_as_running(self):
        self.status = 'running'
        self.started_at = timezone.now()
        self.save()

    def mark_as_success(self, result=None):
        self.status = 'success'
        self.progress = 100
        self.completed_at = timezone.now()
        if result:
            self.result = str(result)
        self.save()

    def mark_as_failed(self, error_message=None):
        self.status = 'failed'
        self.completed_at = timezone.now()
        if error_message:
            self.error_message = str(error_message)
        self.save()

    def update_progress(self, progress):
        self.progress = min(100, max(0, progress))
        self.save()


class TaskLog(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='logs')
    message = models.TextField()
    level = models.CharField(max_length=20, default='INFO')  # INFO, WARNING, ERROR, DEBUG
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['task', '-created_at']),
        ]

    def __str__(self):
        return f"{self.task.title} - {self.level}: {self.message[:50]}"

