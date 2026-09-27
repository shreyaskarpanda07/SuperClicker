import threading
import queue
import time
from typing import Optional, Callable

try:
    import pyttsx3
    TTS_AVAILABLE = True
except ImportError:
    TTS_AVAILABLE = False

try:
    import speech_recognition as sr
    SR_AVAILABLE = True
except ImportError:
    SR_AVAILABLE = False


class VoiceNarrator:
    """
    Non-blocking real-time voice synthesis and speech input.
    Operates in a separate worker thread so audio playback never hitches the UI or animations.
    """
    def __init__(self, config):
        self.config = config
        self.enabled = config.get("audio.enabled", True)
        self.rate = config.get("audio.rate", 175)
        self.volume = config.get("audio.volume", 0.95)
        self.voice_index = config.get("audio.voice_index", 0)

        self._speech_queue = queue.Queue()
        self._running = False
        self._worker_thread = None
        self._is_speaking = False

        if TTS_AVAILABLE and self.enabled:
            self._start_worker()

    def _start_worker(self):
        self._running = True
        self._worker_thread = threading.Thread(target=self._speech_loop, daemon=True)
        self._worker_thread.start()

    def speak(self, text: str):
        """Queues text to be spoken by the personal mentor voice."""
        if not self.enabled or not TTS_AVAILABLE or not text.strip():
            return
        # Clear previous unfinished sentences if new guidance arrives
        with self._speech_queue.mutex:
            self._speech_queue.queue.clear()
        self._speech_queue.put(text)

    def stop(self):
        """Immediately interrupts speech output."""
        with self._speech_queue.mutex:
            self._speech_queue.queue.clear()

    def _speech_loop(self):
        try:
            engine = pyttsx3.init()
            engine.setProperty("rate", self.rate)
            engine.setProperty("volume", self.volume)
            voices = engine.getProperty("voices")
            if voices and self.voice_index < len(voices):
                engine.setProperty("voice", voices[self.voice_index].id)
        except Exception as e:
            print(f"[Voice] Engine init error: {e}")
            return

        while self._running:
            try:
                text = self._speech_queue.get(timeout=0.2)
                self._is_speaking = True
                engine.say(text)
                engine.runAndWait()
                self._is_speaking = False
                self._speech_queue.task_done()
            except queue.Empty:
                continue
            except Exception as e:
                print(f"[Voice] Speak error: {e}")
                self._is_speaking = False


class VoiceListener:
    """
    Push-to-Talk audio input capture.
    Listens while button is held or for a short window, converting speech to query text.
    """
    def __init__(self, config):
        self.config = config
        self.recognizer = sr.Recognizer() if SR_AVAILABLE else None

    def listen_once(self, timeout: int = 5, phrase_time_limit: int = 8) -> Optional[str]:
        if not SR_AVAILABLE or not self.recognizer:
            print("[VoiceListener] SpeechRecognition not available.")
            return None

        try:
            with sr.Microphone() as source:
                print("[VoiceListener] Adjusting for ambient noise...")
                self.recognizer.adjust_for_ambient_noise(source, duration=0.6)
                print("[VoiceListener] Listening for your question...")
                audio = self.recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)
                text = self.recognizer.recognize_google(audio)
                print(f"[VoiceListener] Recognized: '{text}'")
                return text
        except sr.WaitTimeoutError:
            print("[VoiceListener] Timed out waiting for speech.")
            return None
        except sr.UnknownValueError:
            print("[VoiceListener] Could not understand speech audio.")
            return None
        except Exception as e:
            print(f"[VoiceListener] Error capturing audio: {e}")
            return None
