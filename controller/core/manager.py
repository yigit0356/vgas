import asyncio
import importlib
import pkgutil
from typing import Dict
from core.socket import socket_manager
from core.module import BaseModule

class ModuleManager:
    def __init__(self):
        self.modules: Dict[str, BaseModule] = {}
        self.log_history = []
        self.max_logs = 100
        self.socket_manager = socket_manager

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
        import datetime
        now = datetime.datetime.now().strftime("%H:%M:%S")
        
        log_entry = {
            "message": message,
            "level": type,
            "time": now
        }
        
        # Add to history
        self.log_history.append(log_entry)
        if len(self.log_history) > self.max_logs:
            self.log_history.pop(0)

        await socket_manager.broadcast({
            "type": "notification",
            "data": log_entry
        })

    async def update_telemetry(self, data: dict):
        await socket_manager.broadcast({
            "type": "telemetry",
            "data": data
        })

    async def execute_module_command(self, module_name: str, command: str, data: dict = None):
        module = self.modules.get(module_name)
        if module and hasattr(module, 'execute_command'):
            return await module.execute_command(command, data)
        return {"error": f"Module {module_name} not found or doesn't support commands"}

module_manager = ModuleManager()
