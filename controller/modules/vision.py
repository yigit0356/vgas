import asyncio
import io
import time
import httpx
import uuid
import base64
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
        self.workflow_finished = False
        self.current_step = "idle" # camera, ai, audio, idle
        self.status_message = "System Standby - Ready for Command"
        self.last_image = None # Base64 string
        self.last_audio = None # Base64 string
        self.current_workflow_id = None
        # Initialize API Base URL from config
        config_module = self.manager.modules.get("config")
        self.api_base_url = config_module.config.get("base_url", "") if config_module else ""

        if HAS_PYGAME:
            pygame.mixer.init()

        if IS_PI:
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(self.BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    async def update_status(self, status, step=None, has_error=None, finished=None):
        """Sends vision process status to dashboard"""
        if step: self.current_step = step
        if has_error is not None: self.has_error = has_error
        if finished is not None: self.workflow_finished = finished
        self.status_message = status
        
        await self.manager.socket_manager.broadcast({
            "type": "vision_update",
            "data": {
                "status": self.status_message,
                "step": self.current_step,
                "is_processing": self.is_processing,
                "audio_state": self.audio_state,
                "has_error": self.has_error,
                "workflow_finished": self.workflow_finished,
                "assets": {
                    "image": self.last_image,
                    "audio": self.last_audio
                }
            }
        })
        print(f"Vision state updated: {self.current_step}, processing={self.is_processing}, error={self.has_error}")

    def take_a_photo(self):
        try:
            # Using httpx for photo capture too for consistency if needed, but requests is fine for static images
            import requests
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
            if not self.cancel_workflow:
                await self.update_status("Speaking finished", "idle")
        except Exception as e:
            print(f"Audio error: {e}")
            self.audio_state = "idle"

    async def image_to_speech(self, image_obj, workflow_id):
        img_byte_arr = io.BytesIO()
        image_obj.save(img_byte_arr, format='JPEG')
        img_byte_arr.seek(0)
        
        config_module = self.manager.modules.get("config")
        api_key = config_module.config.get("api_key", "") if config_module else ""
        img_data = img_byte_arr.getvalue()

        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                files = {'file': ('image.jpg', img_data, 'image/jpeg')}
                params = {'api_key': api_key, 'id': workflow_id}
                
                response = await client.post(
                    f"{self.api_base_url.rstrip('/')}/api/analyze",
                    files=files,
                    params=params
                )
                
                if response.status_code == 200:
                    return response.content, None
                else:
                    try:
                        error_data = response.json()
                        error_msg = error_data.get("message", response.text)
                    except:
                        error_msg = response.text
                    print(f"API Error: {response.status_code} - {error_msg}")
                    return None, f"API {response.status_code}: {error_msg}"
        except asyncio.CancelledError:
            print(f"Analyze request {workflow_id} was cancelled locally.")
            raise
        except Exception as e:
            print(f"Analyze error: {e}")
            return None, str(e)

    async def cancel_remote_request(self, workflow_id):
        """Tells the web server to stop processing a specific request"""
        if not workflow_id:
            return
        
        print(f"Sending cancellation signal for {workflow_id}...")
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                await client.post(f"{self.api_base_url.rstrip('/')}/api/analyze/cancel", params={'id': workflow_id})
        except Exception as e:
            print(f"Failed to send cancellation to web side: {e}")

    async def process_workflow(self):
        if self.is_processing:
            return
            
        config_module = self.manager.modules.get("config")
        api_key = config_module.config.get("api_key") if config_module else None
        
        if not self.api_base_url or not api_key:
            await self.notify("Operation Aborted: Please configure Base URL and API Key in settings.", "warning")
            return
        
        self.is_processing = True
        self.cancel_workflow = False
        self.has_error = False
        self.workflow_finished = False
        self.current_workflow_id = str(uuid.uuid4())
        
        await self.update_status("Starting Process...", "camera", has_error=False, finished=False)
        await self.notify("Vision process initiated", "info")

        # Step 1: Taking Photo
        if self.cancel_workflow: return await self.reset_states()
        await self.update_status("Capturing image...", "camera")
        loop = asyncio.get_event_loop()
        photo = await loop.run_in_executor(None, self.take_a_photo)
        
        if photo:
            buffered = io.BytesIO()
            photo.save(buffered, format="JPEG")
            self.last_image = base64.b64encode(buffered.getvalue()).decode('utf-8')
            await self.update_status("Image captured and processed", "camera")
            await self.notify("Scene captured: Processing frame for AI analysis", "info")

        if self.cancel_workflow: return await self.reset_states()
        if not photo:
            self.is_processing = False
            await self.update_status("Camera Error: Failed to capture image", has_error=True)
            await self.notify("Camera error: Failed to capture", "warning")
            return

        # Step 2: Analyzing
        await self.update_status("Analyzing via AI...", "ai")
        
        self.analysis_task = asyncio.create_task(self.image_to_speech(photo, self.current_workflow_id))
        
        try:
            audio_data, error_msg = await self.analysis_task
            self.analysis_task = None
        except asyncio.CancelledError:
            print("AI analysis task cancelled.")
            return # reset_states will be called by whatever cancelled it

        if audio_data:
            self.last_audio = base64.b64encode(audio_data).decode('utf-8')
            await self.update_status("AI analysis received", "ai")
            await self.notify("AI Analysis: Insights successfully received from engine", "success")

        if self.cancel_workflow: return await self.reset_states()
        if not audio_data:
            self.is_processing = False
            await self.update_status(f"AI Error: {error_msg}", has_error=True)
            await self.notify(f"AI analysis failed: {error_msg}", "warning")
            return

        # Step 3: Audio Playback
        await self.notify("Audio Response: AI is speaking the report", "info")
        await self.play_audio(audio_data)

        # Finished
        if not self.cancel_workflow:
            self.is_processing = False
            self.workflow_finished = True
            await self.update_status("Analysis Completed Successfully", "idle", finished=True)
            await self.notify("Operation Finished: Full cycle completed successfully", "success")
        else:
            await self.reset_states()

    async def reset_states(self):
        print(f"Resetting vision states. Current ID: {self.current_workflow_id}")
        
        # 1. Signal local cancellation
        self.cancel_workflow = True
        
        # 2. Cancel the analysis task if running
        if self.analysis_task and not self.analysis_task.done():
            self.analysis_task.cancel()
            
        # 3. Propagate to web server
        if self.current_workflow_id:
            asyncio.create_task(self.cancel_remote_request(self.current_workflow_id))

        # 4. Stop audio
        pygame.mixer.music.stop()
        
        self.is_processing = False
        self.audio_state = "idle"
        self.cancel_workflow = False
        self.has_error = False
        self.workflow_finished = False
        self.stop_audio_event = True
        self.current_step = "idle"
        self.status_message = "System Standby - Ready for Command"
        self.last_image = None
        self.last_audio = None
        self.current_workflow_id = None
        self.analysis_task = None
        
        await self.update_status(self.status_message, self.current_step)

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
            
        if command == "audio_stop":
            self.audio_state = "idle"
            pygame.mixer.music.stop()
            await self.update_status("Audio Stopped", self.current_step)
            await self.notify("Audio Playback: Aborted by user", "warning")
            return {"status": "stopped"}

        if command == "reset_vision":
            await self.reset_states()
            await self.notify("System Reset: Engine and assets cleared", "info")
            return {"status": "reset"}

        if command == "audio_backward":
            try:
                pygame.mixer.music.play()
                await self.update_status("Restarting Speech...", "audio")
            except: pass
            return {"status": "restarted"}

        if command == "audio_forward":
            try:
                # Pygame get_pos() returns ms since play() started.
                # set_pos() works in seconds for most formats.
                current_time = pygame.mixer.music.get_pos() / 1000.0
                pygame.mixer.music.set_pos(current_time + 10.0)
                await self.update_status("Skipping Forward...", "audio")
            except: pass
            return {"status": "forwarded"}

        return {"error": "Unknown command"}

    def get_state(self):
        """Returns the current state for syncing with new clients"""
        return {
            "status": self.status_message,
            "step": self.current_step,
            "is_processing": self.is_processing,
            "audio_state": self.audio_state,
            "has_error": self.has_error,
            "workflow_finished": self.workflow_finished,
            "assets": {
                "image": self.last_image,
                "audio": self.last_audio
            }
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


