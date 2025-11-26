import json
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.db import transaction


def send_task_update(task):
    """Send task update via WebSocket"""
    channel_layer = get_channel_layer()
    if channel_layer:
        # Serialize task data in a sync context
        from .serializers import TaskSerializer
        serializer = TaskSerializer(task)
        task_data = serializer.data
        
        async_to_sync(channel_layer.group_send)(
            f"task_{task.id}",
            {
                "type": "task_update",
                "task": task_data
            }
        )
        # Also send to user's personal channel
        async_to_sync(channel_layer.group_send)(
            f"user_{task.user.id}",
            {
                "type": "task_update",
                "task": task_data
            }
        )

