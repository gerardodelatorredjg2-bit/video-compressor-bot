import asyncio
from collections import defaultdict

class QueueManager:
    def __init__(self):
        self.queues = defaultdict(asyncio.Queue)
        self.active_tasks = {}
        self.processing = set()
    
    async def add_to_queue(self, user_id, task):
        await self.queues[user_id].put(task)
    
    def get_queue_position(self, user_id):
        return self.queues[user_id].qsize()
    
    def is_processing(self, user_id):
        return user_id in self.processing
    
    def mark_processing(self, user_id, value=True):
        if value:
            self.processing.add(user_id)
        else:
            self.processing.discard(user_id)
    
    async def get_next_task(self, user_id):
        if self.queues[user_id].empty():
            return None
        try:
            task = self.queues[user_id].get_nowait()
            return task
        except asyncio.QueueEmpty:
            return None
    
    def clear_queue(self, user_id):
        while not self.queues[user_id].empty():
            try:
                self.queues[user_id].get_nowait()
            except:
                break

queue_manager = QueueManager()
