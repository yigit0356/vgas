import asyncio
import psutil
import os
from core.module import BaseModule

class SystemModule(BaseModule):
    def __init__(self, manager):
        super().__init__(manager)
        self.CURRENT_VERSION = "1.2.4"
        self.latest_version = "1.2.4"
        self.update_available = False

    def get_cpu_temp(self):
        # Specific for Raspberry Pi
        try:
            if os.path.exists("/sys/class/thermal/thermal_zone0/temp"):
                with open("/sys/class/thermal/thermal_zone0/temp", "r") as f:
                    return int(f.read()) / 1000
            # Fallback for psutil sensors_temperatures (Desktop)
            temps = psutil.sensors_temperatures()
            if 'cpu_thermal' in temps:
                return temps['cpu_thermal'][0].current
            if 'coretemp' in temps:
                return temps['coretemp'][0].current
        except:
            pass
        return 45.0 # Mock fallback

    async def start(self):
        print("System module started")
        while True:
            try:
                # Battery
                battery = psutil.sensors_battery()
                bat_percent = int(battery.percent) if battery else 85
                power_plugged = battery.power_plugged if battery else True

                # RAM
                ram = psutil.virtual_memory()
                ram_percent = int(ram.percent)
                ram_total = round(ram.total / (1024**3), 1)
                ram_used = round(ram.used / (1024**3), 1)

                # Disk
                disk = psutil.disk_usage('/')
                disk_percent = int(disk.percent)
                disk_total = round(disk.total / (1024**3), 1)
                disk_used = round(disk.used / (1024**3), 1)

                # CPU Temp
                cpu_temp = self.get_cpu_temp()

                await self.manager.update_telemetry({
                    "system": {
                        "battery": {
                            "percent": bat_percent,
                            "charging": power_plugged
                        },
                        "ram": {
                            "percent": ram_percent,
                            "total": ram_total,
                            "used": ram_used
                        },
                        "disk": {
                            "percent": disk_percent,
                            "total": disk_total,
                            "used": disk_used
                        },
                        "cpu": {
                            "temp": round(cpu_temp, 1)
                        },
                        "version": self.CURRENT_VERSION,
                        "latest_version": self.latest_version,
                        "update_available": self.update_available
                    }
                })
                
                if bat_percent < 20:
                    await self.notify("Warning: Battery is low!", "warning")
                
                if cpu_temp > 75:
                    await self.notify("Alert: CPU temperature is high!", "warning")

            except Exception as e:
                print(f"Error in SystemModule: {e}")
                
            await asyncio.sleep(5) # Faster updates for system metrics

    async def check_for_updates(self):
        """Simulates a fake API request to check for the latest version"""
        await asyncio.sleep(2) # Simulate network lag
        # Mocking: Let's say a new version 1.2.5 is available
        self.latest_version = "1.2.5" 
        self.update_available = self.latest_version != self.CURRENT_VERSION
        return {
            "current": self.CURRENT_VERSION,
            "latest": self.latest_version,
            "available": self.update_available
        }

    async def perform_update(self):
        """Placeholder for the update logic"""
        # This will be implemented later
        print("Starting system update...")
        await asyncio.sleep(5)
        print("Update function is currently empty.")
        return {"status": "update_started"}

    async def execute_command(self, command, data=None):
        if command == "check_updates":
            result = await self.check_for_updates()
            return result
        if command == "perform_update":
            result = await self.perform_update()
            return result
        return {"error": "Unknown command"}

    def get_state(self):
        return {
            "version": self.CURRENT_VERSION,
            "latest_version": self.latest_version,
            "update_available": self.update_available
        }

    async def stop(self):
        pass
