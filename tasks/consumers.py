import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.apps import apps


class TaskConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]
        
        if not self.user.is_authenticated:
            await self.close()
            return
        
        # Join user's personal room
        self.user_room = f"user_{self.user.id}"
        await self.channel_layer.group_add(
            self.user_room,
            self.channel_name
        )
        
        await self.accept()
    
    async def disconnect(self, close_code):
        if hasattr(self, 'user_room'):
            await self.channel_layer.group_discard(
                self.user_room,
                self.channel_name
            )
        
        # Leave any task-specific rooms
        if hasattr(self, 'task_rooms'):
            for room in self.task_rooms:
                await self.channel_layer.group_discard(
                    room,
                    self.channel_name
                )
    
    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            message_type = data.get('type')
            
            if message_type == 'subscribe_task':
                task_id = data.get('task_id')
                if task_id:
                    task_room = f"task_{task_id}"
                    if not hasattr(self, 'task_rooms'):
                        self.task_rooms = set()
                    self.task_rooms.add(task_room)
                    
                    await self.channel_layer.group_add(
                        task_room,
                        self.channel_name
                    )
                    
                    # Send current task state
                    task = await self.get_task(task_id)
                    if task and task.user_id == self.user.id:
                        # Serialize task data in async-safe way
                        task_data = await self.serialize_task(task)
                        await self.send(text_data=json.dumps({
                            'type': 'task_update',
                            'task': task_data
                        }))
            
            elif message_type == 'unsubscribe_task':
                task_id = data.get('task_id')
                if task_id and hasattr(self, 'task_rooms'):
                    task_room = f"task_{task_id}"
                    self.task_rooms.discard(task_room)
                    await self.channel_layer.group_discard(
                        task_room,
                        self.channel_name
                    )
        
        except json.JSONDecodeError:
            pass
    
    async def task_update(self, event):
        """Receive task update from group"""
        await self.send(text_data=json.dumps({
            'type': 'task_update',
            'task': event['task']
        }))
    
    @database_sync_to_async
    def get_task(self, task_id):
        try:
            Task = apps.get_model('tasks', 'Task')
            return Task.objects.get(id=task_id)
        except Exception:
            return None
    
    @database_sync_to_async
    def serialize_task(self, task):
        """Serialize task in a sync context"""
        from .serializers import TaskSerializer
        serializer = TaskSerializer(task)
        return serializer.data

