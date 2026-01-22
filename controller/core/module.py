from abc import ABC, abstractmethod

class BaseModule(ABC):
    def __init__(self, manager):
        self.manager = manager
        self.name = self.__class__.__name__

    @abstractmethod
    async def start(self):
        pass

    @abstractmethod
    async def stop(self):
        pass

    async def notify(self, message: str, type: str = "info"):
        """Sends a notification to the dashboard"""
        await self.manager.send_notification(message, type)
