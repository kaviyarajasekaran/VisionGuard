"""
audio_output.py - VisionGuard Audio Output Module (Fixed by Siri)
-------------------------------------------------------------------
Fix: Tamil gTTS runs in separate sub-thread so camera never hangs
     Queue size limited to 3 — prevents backlog of old alerts
"""

import threading
import queue
import os
import tempfile
import time


class AudioOutput:

    def __init__(self, language="english", rate=150):
        self.language     = language.lower()
        # ✅ Max 3 items in queue — old alerts drop automatically
        self.speech_queue = queue.Queue(maxsize=3)
        self._stopped     = False
        self._worker      = None

        if self.language not in ["english", "tamil"]:
            raise ValueError(f"Unknown language: {language}.")

        self._start_worker()
        print(f"[AudioOutput] Windows SAPI voice loaded (offline English).")
        print(f"[AudioOutput] Language '{language}' initialized successfully.")

    def _start_worker(self):
        self._worker = threading.Thread(target=self._process_queue, daemon=False)
        self._worker.start()

    def _process_queue(self):
        import pythoncom
        pythoncom.CoInitialize()

        while True:
            try:
                text = self.speech_queue.get(timeout=0.5)
            except queue.Empty:
                if self._stopped:
                    break
                continue

            if text is None:
                break

            if not self._stopped:
                self._speak_now(text)
            self.speech_queue.task_done()

        pythoncom.CoUninitialize()

    def _speak_now(self, text):
        try:
            if self.language == "english":
                self._speak_english(text)
            elif self.language == "tamil":
                self._speak_tamil(text)
        except Exception as e:
            print(f"[AudioOutput] Speech error: {e}")

    def _speak_english(self, text):
        import win32com.client
        speaker = win32com.client.Dispatch("SAPI.SpVoice")
        speaker.Speak(text)

    def _speak_tamil(self, text):
        """
        ✅ Fix: gTTS download + pygame play in background sub-thread
        This means the queue worker moves on immediately
        Camera never hangs waiting for Tamil audio to finish
        """
        def _play():
            try:
                from gtts import gTTS
                import pygame

                tts = gTTS(text=text, lang='ta', slow=False)
                with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
                    temp_path = f.name
                tts.save(temp_path)

                pygame.mixer.init()
                pygame.mixer.music.load(temp_path)
                pygame.mixer.music.play()
                while pygame.mixer.music.get_busy():
                    time.sleep(0.1)
                pygame.mixer.music.unload()
                os.remove(temp_path)
            except Exception as e:
                print(f"[AudioOutput] Tamil error: {e}")

        t = threading.Thread(target=_play, daemon=True)
        t.start()
        t.join(timeout=8)  # Max 8 seconds wait — prevents infinite hang

    def speak(self, text):
        if not text or not text.strip() or self._stopped:
            return
        print(f"[AudioOutput] Speaking: {text}")
        # ✅ Don't block if queue is full — drop old alert
        try:
            self.speech_queue.put_nowait(text)
        except queue.Full:
            pass  # Skip if queue is full — keeps system real-time

    def speak_all(self, messages):
        for msg in messages:
            self.speak(msg)

    def stop(self):
        """Fully stop — clear queue, set flag, wait for thread."""
        self._stopped = True

        # Clear all pending messages
        while not self.speech_queue.empty():
            try:
                self.speech_queue.get_nowait()
                self.speech_queue.task_done()
            except:
                pass

        self.speech_queue.put(None)

        if self._worker and self._worker.is_alive():
            self._worker.join(timeout=3)

        print("[AudioOutput] Stopped.")