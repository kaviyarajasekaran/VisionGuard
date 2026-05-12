"""
sos_module.py - VisionGuard SOS Emergency Module
------------------------------------------------
Press 'O' key to trigger SOS.

Features:
1. Demo mode -> fixed college location
2. Speaks emergency alert
3. Sends WhatsApp SOS alert automatically
4. Logs event

Future:
- Raspberry Pi
- GPS
- GSM module
"""

import time
import threading

# ============================================================
# CONFIGURATION
# ============================================================
SIMULATE_HARDWARE = True

# Demo mode for project presentation
DEMO_MODE = True

# Er. Perumal Manimekalai College Of Engineering
COLLEGE_LOCATION = (12.6750201, 77.9683159)
EMERGENCY_CONTACTS = [
    "+918489764591",   # Replace if needed
]

GPS_PORT = "/dev/ttyAMA0"
GPS_BAUD = 9600
GSM_PORT = "/dev/ttyUSB0"
GSM_BAUD = 9600

SOS_COOLDOWN_SECONDS = 30
# ============================================================


class SOSModule:

    def __init__(self, speaker=None, language="english", simulate=SIMULATE_HARDWARE):
        self.speaker = speaker
        self.language = language
        self.simulate = simulate
        self.last_sos_time = 0
        self.gps_serial = None
        self.gsm_serial = None
        self.current_location = None

        if not simulate:
            self._init_gps()
            self._init_gsm()
            self._start_gps_thread()
            print("[SOS] Hardware mode initialized")
        else:
            print("[SOS] Laptop simulation mode initialized")

    def update_speaker(self, speaker, language):
        self.speaker = speaker
        self.language = language

    # --------------------------------------------------------
    # HARDWARE GPS (future use)
    # --------------------------------------------------------
    def _init_gps(self):
        try:
            import serial
            self.gps_serial = serial.Serial(GPS_PORT, GPS_BAUD, timeout=1)
            print(f"[SOS] GPS connected on {GPS_PORT}")
        except Exception as e:
            print(f"[SOS] GPS init failed: {e}")

    def _init_gsm(self):
        try:
            import serial
            self.gsm_serial = serial.Serial(GSM_PORT, GSM_BAUD, timeout=3)
            print(f"[SOS] GSM connected on {GSM_PORT}")
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
                            self.current_location = (
                                msg.latitude,
                                msg.longitude
                            )
                        except:
                            pass

                time.sleep(0.5)

        except Exception as e:
            print(f"[SOS] GPS error: {e}")

    # --------------------------------------------------------
    # LOCATION
    # --------------------------------------------------------
    def get_location(self):
        """
        Demo mode -> fixed college coordinates
        Live mode -> IP location
        """
        if DEMO_MODE:
            print(f"[SOS] Demo mode location: {COLLEGE_LOCATION}")
            return COLLEGE_LOCATION

        if self.simulate:
            try:
                import geocoder
                g = geocoder.ip("me")

                if g.latlng:
                    print(f"[SOS] Live location found: {g.latlng}")
                    return tuple(g.latlng)

            except Exception as e:
                print(f"[SOS] Location error: {e}")

        return None

    # --------------------------------------------------------
    # MAIN SOS
    # --------------------------------------------------------
    def trigger_sos(self):

        now = time.time()

        if now - self.last_sos_time < SOS_COOLDOWN_SECONDS:
            remaining = int(SOS_COOLDOWN_SECONDS - (now - self.last_sos_time))
            print(f"[SOS] Wait {remaining}s before retry")
            return

        self.last_sos_time = now
        print("\n[SOS] ===== SOS TRIGGERED =====")

        location = self.get_location()

        if location:
            lat, lon = location
            loc_str = f"Lat {lat:.5f}, Lon {lon:.5f}"
            maps_link = f"https://maps.google.com/?q={lat},{lon}"
        else:
            loc_str = "Location unavailable"
            maps_link = "Unavailable"

        print(f"[SOS] {loc_str}")

        # Voice output
        if self.speaker:
            if self.language.lower() == "tamil":
                msg = "அவசரநிலை! உதவி தேவை. அவசர தகவல் அனுப்பப்படுகிறது."
            else:
                msg = "Emergency activated. Sending alert now."

            self.speaker.speak(msg)

        emergency_message = (
            "SOS ALERT - VisionGuard\n"
            "User needs immediate help!\n"
            f"Location: {loc_str}\n"
            f"Map: {maps_link}"
        )

        for number in EMERGENCY_CONTACTS:
            self._send_alert(number, emergency_message)

        self._log(location, emergency_message)

    # --------------------------------------------------------
    # SEND WHATSAPP ALERT
    # --------------------------------------------------------
    def _send_alert(self, number, message):

        if self.simulate:
            try:
                import pywhatkit as kit
                import pyautogui
                import time

                print(f"[SOS] Opening WhatsApp for {number}")

                kit.sendwhatmsg_instantly(
                    phone_no=number,
                    message=message,
                    wait_time=20,
                    tab_close=False,
                    close_time=3
                )

                # Wait longer for browser + whatsapp loading
                time.sleep(15)

                # Click once to focus browser
                pyautogui.click()

                time.sleep(2)

                # Press enter to send
                pyautogui.press("enter")

                print(f"[SOS] Message sent successfully to {number}")

            except Exception as e:
                print(f"[SOS] WhatsApp error: {e}")

            return
    # --------------------------------------------------------
    # LOGGING
    # --------------------------------------------------------
    def _log(self, location, message):
        try:
            with open("sos_log.txt", "a", encoding="utf-8") as f:
                timestamp = time.strftime("%Y-%m-%d %H:%M:%S")

                f.write(f"\n[{timestamp}] SOS TRIGGERED\n")
                f.write(f"Location: {location}\n")
                f.write(f"Message:\n{message}\n")
                f.write("-" * 50 + "\n")

            print("[SOS] Logged successfully")

        except Exception as e:
            print(f"[SOS] Log error: {e}")
