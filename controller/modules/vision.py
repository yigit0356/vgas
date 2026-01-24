import asyncio
import io
import time
import requests
from PIL import Image
from core.module import BaseModule

# Mock GPIO for non-Pi environments
try:
    import RPi.GPIO as GPIO
    IS_PI = True
except (ImportError, RuntimeError):
    class MockGPIO:
        BCM = 'BCM'
        IN = 'IN'
        PUD_UP = 'PUD_UP'
        LOW = 'LOW'
        def setmode(self, mode): pass
        def setup(self, pin, mode, pull_up_down=None): pass
        def input(self, pin): return 1 # Always return HIGH (not pressed)
        def cleanup(self): pass
    
    GPIO = MockGPIO()
    IS_PI = False

try:
    import pygame
    HAS_PYGAME = True
except ImportError:
    HAS_PYGAME = False

class VisionModule(BaseModule):
    def __init__(self, manager):
        super().__init__(manager)
        self.BUTTON_PIN = 17
        self.is_processing = False
        self.audio_state = "idle" # idle, playing, paused
        self.stop_audio_event = False
        self.cancel_workflow = False
        self.has_error = False
        self.current_step = "idle" # camera, ai, audio, idle

        if HAS_PYGAME:
            pygame.mixer.init()

        if IS_PI:
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(self.BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    async def update_status(self, status, step=None, has_error=None):
        """Sends vision process status to dashboard"""
        if step: self.current_step = step
        if has_error is not None: self.has_error = has_error
        
        await self.manager.socket_manager.broadcast({
            "type": "vision_update",
            "data": {
                "status": status,
                "step": self.current_step,
                "is_processing": self.is_processing,
                "audio_state": self.audio_state,
                "has_error": self.has_error
            }
        })

    def take_a_photo(self):
        try:
            # Using the URL from user's code
            response = requests.get('https://cdn.dont-ping.me/api/🐭🦕🙃👻🤖.JPEG', timeout=10)
            if response.status_code == 200:
                return Image.open(io.BytesIO(response.content))
            return None
        except Exception as e:
            print(f"Photo error: {e}")
            return None

    async def play_audio(self, audio_content):
        if not HAS_PYGAME:
            print("Pygame not available, skipping audio play.")
            return
        
        try:
            audio_stream = io.BytesIO(audio_content)
            pygame.mixer.music.load(audio_stream)
            pygame.mixer.music.play()
            
            self.audio_state = "playing"
            self.stop_audio_event = False
            
            await self.update_status("Speaking...", "audio")

            while pygame.mixer.music.get_busy() or self.audio_state == "paused":
                if self.stop_audio_event or self.cancel_workflow:
                    pygame.mixer.music.stop()
                    break
                await asyncio.sleep(0.1)
            
            self.audio_state = "idle"
            self.stop_audio_event = False
        except Exception as e:
            print(f"Audio error: {e}")
            self.audio_state = "idle"

    async def image_to_speech(self, image_obj):
        img_byte_arr = io.BytesIO()
        image_obj.save(img_byte_arr, format='JPEG')
        img_byte_arr.seek(0)
        
        config_module = self.manager.modules.get("config")
        api_key = config_module.config.get("api_key", "") if config_module else ""
        
        files = {'file': ('image.jpg', img_byte_arr, 'image/jpeg')}
        params = {'api_key': api_key}
        
        try:
            response = requests.post(
                'https://vgas.up.railway.app/api/analyze', 
                files=files,
                params=params,
                timeout=120
            )
            if response.status_code == 200:
                return response.content
            else:
                print(f"API Error: {response.status_code} - {response.text}")
                return None
        except Exception as e:
            print(f"Analyze error: {e}")
            return None

    async def process_workflow(self):
        if self.is_processing:
            return
        
        self.is_processing = True
        self.cancel_workflow = False
        await self.update_status("Starting Process...", "camera")
        await self.notify("Vision process initiated", "info")

        # Step 1: Taking Photo
        if self.cancel_workflow: return self.reset_states()
        await self.update_status("Capturing image...", "camera")
        loop = asyncio.get_event_loop()
        photo = await loop.run_in_executor(None, self.take_a_photo)
        
        if self.cancel_workflow: return self.reset_states()
        if not photo:
            self.is_processing = False
            await self.update_status("Camera Error: Failed to capture image", has_error=True)
            await self.notify("Camera error: Failed to capture", "warning")
            return

        # Step 2: Analyzing
        await self.update_status("Analyzing via AI...", "ai")
        audio_data = await self.image_to_speech(photo)
        
        if self.cancel_workflow: return self.reset_states()
        if not audio_data:
            self.is_processing = False
            await self.update_status("AI Error: Failed to analyze image via API", has_error=True)
            await self.notify("AI error: Failed to analyze image", "warning")
            return

        # Step 3: Audio Playback
        await self.play_audio(audio_data)

        # Finished
        if not self.cancel_workflow:
            self.is_processing = False
            await self.update_status("Analysis Completed", "idle")
            await self.notify("Vision process completed", "success")
        else:
            self.reset_states()

    def reset_states(self):
        self.is_processing = False
        self.audio_state = "idle"
        self.cancel_workflow = False
        self.has_error = False
        self.stop_audio_event = True
        self.current_step = "idle"
        pygame.mixer.music.stop()
        asyncio.create_task(self.update_status("", "idle"))

    async def execute_command(self, command, data=None):
        print(f"Vision command received: {command}")
        if command == "trigger_vision":
            asyncio.create_task(self.process_workflow())
            return {"status": "triggered"}
            
        if command == "audio_pause":
            if self.audio_state == "playing":
                pygame.mixer.music.pause()
                self.audio_state = "paused"
                await self.update_status("Speaking Paused", "audio")
            return {"status": self.audio_state}
            
        if command == "audio_resume":
            if self.audio_state == "paused":
                pygame.mixer.music.unpause()
                self.audio_state = "playing"
                await self.update_status("Speaking...", "audio")
            return {"status": self.audio_state}
            
        if command == "audio_stop" or command == "reset_vision":
            self.cancel_workflow = True
            self.reset_states()
            return {"status": "reset"}

        if command == "audio_backward":
            try:
                pygame.mixer.music.rewind()
            except: pass
            return {"status": "rewinded"}

        return {"error": "Unknown command"}

    def get_state(self):
        """Returns the current state for syncing with new clients"""
        return {
            "status": "System Ready" if self.current_step == "idle" and not self.is_processing else "Active",
            "step": self.current_step,
            "is_processing": self.is_processing,
            "audio_state": self.audio_state,
            "has_error": self.has_error
        }

    async def start(self):
        print("Vision module started")
        while True:
            # Check physical button button state
            if IS_PI:
                try:
                    if GPIO.input(self.BUTTON_PIN) == GPIO.LOW:
                        await self.process_workflow()
                        await asyncio.sleep(2) # Debounce/Wait
                except:
                    pass
            
            await asyncio.sleep(0.1)

    async def stop(self):
        if IS_PI:
            GPIO.cleanup()
