from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from django.db.models import Count, Q
from datetime import timedelta
from .models import Task, TaskLog
from .serializers import TaskSerializer, TaskCreateSerializer
from .tasks import process_file_task, scraping_task, generate_report_task
from celery import current_app


class TaskViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        queryset = Task.objects.filter(user=user).prefetch_related('logs')
        
        # Filter by status
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        # Filter by task_type
        task_type = self.request.query_params.get('task_type')
        if task_type:
            queryset = queryset.filter(task_type=task_type)
        
        return queryset
    
    def get_serializer_class(self):
        if self.action == 'create':
            return TaskCreateSerializer
        return TaskSerializer
    
    def perform_create(self, serializer):
        task = serializer.save(user=self.request.user)
        
        # Schedule task if scheduled_at is set
        if task.scheduled_at and task.scheduled_at > timezone.now():
            # For scheduled tasks, we'd use celery beat, but for simplicity
            # we'll just store it and let the user trigger it manually
            pass
        else:
            # Execute immediately
            self._execute_task(task)
    
    def _execute_task(self, task):
        """Execute the appropriate Celery task based on task type"""
        if task.task_type == 'file_processing':
            process_file_task.delay(task.id)
        elif task.task_type == 'scraping':
            scraping_task.delay(task.id)
        elif task.task_type == 'report_generation':
            generate_report_task.delay(task.id)
    
    @action(detail=True, methods=['post'])
    def retry(self, request, pk=None):
        """Retry a failed task"""
        task = self.get_object()
        
        if task.status not in ['failed', 'success']:
            return Response(
                {'error': 'Can only retry failed or completed tasks'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if task.retry_count >= task.max_retries:
            return Response(
                {'error': 'Maximum retries reached'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Reset task
        task.status = 'pending'
        task.progress = 0
        task.error_message = None
        task.retry_count += 1
        task.started_at = None
        task.completed_at = None
        task.celery_task_id = None
        task.save()
        
        # Execute
        self._execute_task(task)
        
        return Response(TaskSerializer(task).data)
    
    @action(detail=True, methods=['get'])
    def logs(self, request, pk=None):
        """Get logs for a task"""
        task = self.get_object()
        logs = task.logs.all()[:100]  # Limit to 100 most recent
        from .serializers import TaskLogSerializer
        return Response(TaskLogSerializer(logs, many=True).data)
    
    @action(detail=False, methods=['get'])
    def analytics(self, request):
        """Get analytics for user's tasks"""
        user = request.user
        tasks = Task.objects.filter(user=user)
        
        total = tasks.count()
        by_status = dict(tasks.values('status').annotate(count=Count('id')).values_list('status', 'count'))
        by_type = dict(tasks.values('task_type').annotate(count=Count('id')).values_list('task_type', 'count'))
        
        # Recent activity (last 7 days)
        week_ago = timezone.now() - timedelta(days=7)
        recent = tasks.filter(created_at__gte=week_ago).count()
        
        # Success rate
        success_count = tasks.filter(status='success').count()
        success_rate = (success_count / total * 100) if total > 0 else 0
        
        return Response({
            'total_tasks': total,
            'by_status': by_status,
            'by_type': by_type,
            'recent_tasks': recent,
            'success_rate': round(success_rate, 2),
        })


class AdminAnalyticsViewSet(viewsets.ViewSet):
    """Admin-only analytics dashboard"""
    permission_classes = [IsAuthenticated]
    
    def list(self, request):
        if not request.user.is_staff:
            return Response(
                {'error': 'Admin access required'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        tasks = Task.objects.all()
        
        total = tasks.count()
        by_status = dict(tasks.values('status').annotate(count=Count('id')).values_list('status', 'count'))
        by_type = dict(tasks.values('task_type').annotate(count=Count('id')).values_list('task_type', 'count'))
        
        # Active workers
        inspect = current_app.control.inspect()
        active_workers = len(inspect.active() or {})
        
        # Recent activity
        week_ago = timezone.now() - timedelta(days=7)
        recent = tasks.filter(created_at__gte=week_ago).count()
        
        # Users with most tasks
        top_users = tasks.values('user__username').annotate(
            count=Count('id')
        ).order_by('-count')[:10]
        
        return Response({
            'total_tasks': total,
            'by_status': by_status,
            'by_type': by_type,
            'active_workers': active_workers,
            'recent_tasks': recent,
            'top_users': list(top_users),
        })

