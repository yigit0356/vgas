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
        return {"api_key": ""}

    def save_config(self, new_config):
        self.config.update(new_config)
        with open(self.config_path, 'w') as f:
            json.dump(self.config, f)
        return self.config

    async def start(self):
        print("Config module loaded")

    async def stop(self):
        pass
