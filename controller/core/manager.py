import asyncio
import importlib
import pkgutil
from typing import Dict
from core.socket import socket_manager
from core.module import BaseModule

class ModuleManager:
    def __init__(self):
        self.modules: Dict[str, BaseModule] = {}

    async def load_modules(self, modules_package):
        """Dynamically loads all modules in the modules directory"""
        for _, name, is_pkg in pkgutil.iter_modules(modules_package.__path__):
            full_module_name = f"modules.{name}"
            module = importlib.import_module(full_module_name)
            
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if (isinstance(attr, type) and 
                    issubclass(attr, BaseModule) and 
                    attr is not BaseModule):
                    
                    instance = attr(self)
                    self.modules[name] = instance
                    print(f"Loaded module: {name}")

    async def start_all(self):
        for name, module in self.modules.items():
            asyncio.create_task(module.start())

    async def send_notification(self, message: str, type: str = "info"):
        await socket_manager.broadcast({
            "type": "notification",
            "data": {
                "message": message,
                "level": type
            }
        })

    async def update_telemetry(self, data: dict):
        await socket_manager.broadcast({
            "type": "telemetry",
            "data": data
        })

module_manager = ModuleManager()
