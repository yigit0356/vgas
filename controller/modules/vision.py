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
        if IS_PI:
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(self.BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    async def update_status(self, status, step=None):
        """Sends vision process status to dashboard"""
        await self.manager.socket_manager.broadcast({
            "type": "vision_update",
            "data": {
                "status": status,
                "step": step,
                "is_processing": self.is_processing
            }
        })

    def take_a_photo(self):
        try:
            # Using the URL from user's code
            response = requests.get('https://cdn.dont-ping.me/api/🐭🦕🙃👻🤖.JPEG')
            if response.status_code == 200:
                return Image.open(io.BytesIO(response.content))
            return None
        except Exception as e:
            print(f"Photo error: {e}")
            return None

    def play_audio(self, audio_content):
        if not HAS_PYGAME:
            print("Pygame not available, skipping audio play.")
            return
        try:
            audio_stream = io.BytesIO(audio_content)
            pygame.mixer.init()
            pygame.mixer.music.load(audio_stream)
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy():
                time.sleep(0.1)
            pygame.mixer.quit()
        except Exception as e:
            print(f"Audio error: {e}")

    async def image_to_speech(self, image_obj):
        img_byte_arr = io.BytesIO()
        image_obj.save(img_byte_arr, format='PNG')
        img_byte_arr.seek(0)
        files = {'file': ('image.png', img_byte_arr, 'image/png')}
        
        try:
            # Using the URL from user's code
            response = requests.post('https://vgas.up.railway.app/api/analyze', files=files)
            if response.status_code == 200:
                return response.content
            return None
        except Exception as e:
            print(f"Analyze error: {e}")
            return None

    async def process_workflow(self):
        if self.is_processing:
            return
        
        self.is_processing = True
        await self.update_status("Processing started", "start")
        await self.notify("Vision process started", "info")

        # Step 1: Taking Photo
        await self.update_status("Capturing image...", "camera")
        loop = asyncio.get_event_loop()
        photo = await loop.run_in_executor(None, self.take_a_photo)
        
        if not photo:
            self.is_processing = False
            await self.update_status("Failed to capture image", "error")
            await self.notify("Camera error: Failed to capture", "warning")
            return

        # Step 2: Analyzing
        await self.update_status("Analyzing via API...", "ai")
        audio_data = await self.image_to_speech(photo)
        
        if not audio_data:
            self.is_processing = False
            await self.update_status("AI analysis failed", "error")
            await self.notify("AI error: Failed to analyze image", "warning")
            return

        # Step 3: Audio Playback
        await self.update_status("Playing audio response...", "audio")
        await loop.run_in_executor(None, self.play_audio, audio_data)

        # Finished
        self.is_processing = False
        await self.update_status("Ready", "idle")
        await self.notify("Vision process finished successfully", "success")

    async def start(self):
        print("Vision module started")
        while True:
            # Check button state
            if IS_PI:
                if GPIO.input(self.BUTTON_PIN) == GPIO.LOW:
                    await self.process_workflow()
                    await asyncio.sleep(2) # Debounce/Wait
            
            await asyncio.sleep(0.1)

    async def stop(self):
        if IS_PI:
            GPIO.cleanup()
