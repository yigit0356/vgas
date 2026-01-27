import json
import os
from core.module import BaseModule

class ConfigModule(BaseModule):
    def __init__(self, manager):
        super().__init__(manager)
        self.config_path = "config.json"
        self.config = self.load_config()

    def load_config(self):
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r') as f:
                    return json.load(f)
            except:
                pass
        return {
            "api_key": "",
            "base_url": ""
        }

    def save_config(self, new_config):
        self.config.update(new_config)
        with open(self.config_path, 'w') as f:
            json.dump(self.config, f)
            
        # Push update to other modules if they have api_base_url attribute
        new_base_url = self.config.get("base_url")
        if new_base_url:
            for module in self.manager.modules.values():
                if hasattr(module, "api_base_url"):
                    module.api_base_url = new_base_url
                    print(f"Propagated new base_url to {module.__class__.__name__}")
                    
        return self.config

    async def start(self):
        print("Config module loaded")

    async def stop(self):
        pass
