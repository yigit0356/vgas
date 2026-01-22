import asyncio
import psutil
import os
from core.module import BaseModule

class SystemModule(BaseModule):
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

                # CPU Temp
                cpu_temp = self.get_cpu_temp()

                await self.manager.update_telemetry({
                    "system": {
                        "battery": {
                            "percent": bat_percent,
                            "charging": power_plugged
                        },
                        "ram": {
                            "percent": ram_percent
                        },
                        "cpu": {
                            "temp": round(cpu_temp, 1)
                        }
                    }
                })
                
                if bat_percent < 20:
                    await self.notify("Warning: Battery is low!", "warning")
                
                if cpu_temp > 75:
                    await self.notify("Alert: CPU temperature is high!", "warning")

            except Exception as e:
                print(f"Error in SystemModule: {e}")
                
            await asyncio.sleep(5) # Faster updates for system metrics

    async def stop(self):
        pass
