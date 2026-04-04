"""
sos_module.py - VisionGuard SOS Emergency Module
--------------------------------------------------
Press 'O' key to trigger SOS.

What happens:
  1. Gets GPS location (simulated on laptop)
  2. Speaks emergency alert in current language (English or Tamil)
  3. Sends SMS to emergency contacts via SIM800L (simulated on laptop)
  4. Logs event to sos_log.txt

Set SIMULATE_HARDWARE = False on Raspberry Pi with real GPS + SIM800L.
"""

import time
import threading

# ============================================================
# EDIT THESE BEFORE DEPLOYMENT ON RASPBERRY PI
# ============================================================
SIMULATE_HARDWARE = True   # Keep True on laptop. Set False on Pi.

EMERGENCY_CONTACTS = [
    "+91XXXXXXXXXX",   # Replace with real number
    "+91XXXXXXXXXX",   # Second contact
]

GPS_PORT = "/dev/ttyAMA0"   # NEO-6M on Raspberry Pi
GPS_BAUD = 9600
GSM_PORT = "/dev/ttyUSB0"   # SIM800L on Raspberry Pi
GSM_BAUD = 9600
SOS_COOLDOWN_SECONDS = 30
# ============================================================


class SOSModule:

    def __init__(self, speaker=None, language="english", simulate=SIMULATE_HARDWARE):
        """
        Args:
            speaker:  AudioOutput instance (the current active speaker)
            language: "english" or "tamil"
            simulate: True = laptop mode, no real hardware
        """
        self.speaker          = speaker
        self.language         = language
        self.simulate         = simulate
        self.last_sos_time    = 0
        self.gps_serial       = None
        self.gsm_serial       = None
        self.current_location = None

        if not simulate:
            self._init_gps()
            self._init_gsm()
            self._start_gps_thread()
            print("[SOS] Hardware mode — GPS and GSM initialized.")
        else:
            print("[SOS] SIMULATE mode — no real GPS/GSM hardware used.")

    def update_speaker(self, speaker, language):
        """Call this when user switches language, so SOS speaks in new language."""
        self.speaker  = speaker
        self.language = language

    def _init_gps(self):
        try:
            import serial
            self.gps_serial = serial.Serial(GPS_PORT, GPS_BAUD, timeout=1)
            print(f"[SOS] GPS connected: {GPS_PORT}")
        except Exception as e:
            print(f"[SOS] GPS init failed: {e}")

    def _init_gsm(self):
        try:
            import serial
            self.gsm_serial = serial.Serial(GSM_PORT, GSM_BAUD, timeout=3)
            time.sleep(1)
            self.gsm_serial.write(b"AT\r\n")
            resp = self.gsm_serial.read(64).decode(errors="ignore")
            print(f"[SOS] GSM: {'OK' if 'OK' in resp else 'no response'}")
        except Exception as e:
            print(f"[SOS] GSM init failed: {e}")

    def _start_gps_thread(self):
        t = threading.Thread(target=self._gps_loop, daemon=True)
        t.start()

    def _gps_loop(self):
        try:
            import pynmea2
            while True:
                if self.gps_serial and self.gps_serial.in_waiting:
                    raw = self.gps_serial.readline().decode(errors="ignore").strip()
                    if raw.startswith(("$GNGLL", "$GPGLL")):
                        try:
                            msg = pynmea2.parse(raw)
                            self.current_location = (msg.latitude, msg.longitude)
                        except Exception:
                            pass
                time.sleep(0.5)
        except Exception as e:
            print(f"[SOS] GPS thread error: {e}")

    def get_location(self):
        """Returns (lat, lon) or None. Returns simulated location on laptop."""
        if self.simulate:
            return (11.4472, 77.6873)   # Change to your actual location
        return self.current_location

    def trigger_sos(self):
        """Call this when SOS key/button is pressed."""
        now = time.time()
        if now - self.last_sos_time < SOS_COOLDOWN_SECONDS:
            wait = int(SOS_COOLDOWN_SECONDS - (now - self.last_sos_time))
            print(f"[SOS] Cooldown — try again in {wait}s")
            return

        self.last_sos_time = now
        print("\n[SOS] *** SOS TRIGGERED ***")

        # Get location
        location = self.get_location()
        if location:
            lat, lon  = location
            loc_str   = f"Lat {lat:.5f}, Lon {lon:.5f}"
            maps_link = f"https://maps.google.com/?q={lat},{lon}"
        else:
            loc_str   = "Location not available"
            maps_link = "GPS not ready"
        print(f"[SOS] Location: {loc_str}")

        # Speak alert in current language
        if self.speaker:
            if self.language == "tamil":
                msg = "அவசரநிலை! உதவி தேவை. அவசர தொடர்புக்கு அனுப்புகிறேன்."
            else:
                msg = "Emergency! S O S activated. Sending alert to emergency contacts."
            self.speaker.speak(msg)

        # SMS content
        sms = (
            f"SOS ALERT - VisionGuard\n"
            f"User needs immediate help!\n"
            f"Location: {loc_str}\n"
            f"Map: {maps_link}"
        )
        for number in EMERGENCY_CONTACTS:
            self._send_sms(number, sms)

        self._log(location, sms)

    def _send_sms(self, number, message):
        if self.simulate:
            print(f"[SOS] [SIMULATED SMS → {number}]")
            print(f"[SOS] {message}")
            return
        if not self.gsm_serial:
            print("[SOS] Cannot send — GSM not connected")
            return
        try:
            self.gsm_serial.write(b"AT+CMGF=1\r\n")
            time.sleep(0.5)
            self.gsm_serial.write(f'AT+CMGS="{number}"\r\n'.encode())
            time.sleep(0.5)
            self.gsm_serial.write((message + "\x1A").encode())
            time.sleep(3)
            resp = self.gsm_serial.read(512).decode(errors="ignore")
            print(f"[SOS] SMS {'sent' if '+CMGS' in resp else 'failed'} to {number}")
        except Exception as e:
            print(f"[SOS] SMS error: {e}")

    def _log(self, location, message):
        try:
            with open("sos_log.txt", "a") as f:
                ts = time.strftime("%Y-%m-%d %H:%M:%S")
                f.write(f"\n[{ts}] SOS TRIGGERED\n")
                f.write(f"Location: {location}\n")
                f.write(f"Message:\n{message}\n")
                f.write("-" * 40 + "\n")
            print("[SOS] Logged to sos_log.txt")
        except Exception as e:
            print(f"[SOS] Log error: {e}")
