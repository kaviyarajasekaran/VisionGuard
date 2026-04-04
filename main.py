"""
main.py - VisionGuard: AI-Based Context-Aware Smart Assistive System
----------------------------------------------------------------------
Controls:
  E = English voice
  T = Tamil voice
  S = Scene description
  O = SOS emergency alert         ← NEW
  P = Search nearby places        ← NEW
  Q = Quit
"""

import cv2
import time
import threading

from object_detection    import ObjectDetector
from distance_estimation import DistanceEstimator
from ocr_module          import OCRModule
from context_engine      import ContextEngine
from audio_output        import AudioOutput
from sos_module          import SOSModule        # NEW
from nearby_places       import NearbyPlaces     # NEW

# ===================================================
YOLO_MODEL           = "yolov8n.pt"
CONFIDENCE_THRESHOLD = 0.5
TTS_LANGUAGE         = "english"
OCR_FRAME_INTERVAL   = 5
WEBCAM_INDEX         = 0
WINDOW_NAME          = "VisionGuard | E=English  T=Tamil  S=Scene  O=SOS  P=Places  Q=Quit"
# ===================================================

ocr_result = {"text": "", "lock": threading.Lock()}


def ocr_worker(ocr_module, frame, result_store):
    text = ocr_module.extract_text(frame)
    with result_store["lock"]:
        result_store["text"] = text


def make_speaker(language):
    """Create a fresh speaker — always clean."""
    return AudioOutput(language=language)


def main():
    print("=" * 52)
    print("   VisionGuard: Assistive Vision System")
    print("=" * 52)
    print("   E=English | T=Tamil | S=Scene | O=SOS | P=Places | Q=Quit")
    print("=" * 52)

    print("\n[Main] Initializing modules...")
    detector  = ObjectDetector(model_path=YOLO_MODEL, confidence_threshold=CONFIDENCE_THRESHOLD)
    estimator = DistanceEstimator()
    ocr       = OCRModule(language="eng")

    current_language = [TTS_LANGUAGE]
    context  = ContextEngine(cooldown=5, language=current_language[0])

    # Use a list so we can replace speaker inside loop
    speaker  = [make_speaker(current_language[0])]

    # NEW — SOS and nearby places modules
    sos    = SOSModule(speaker=speaker[0], language=current_language[0], simulate=True)
    places = NearbyPlaces(speaker=speaker[0], language=current_language[0])

    print("[Main] All modules initialized.\n")
    speaker[0].speak("VisionGuard system started. Camera is active.")

    cap = cv2.VideoCapture(WEBCAM_INDEX)
    if not cap.isOpened():
        print("[Main] ERROR: Could not open webcam.")
        return

    print("[Main] Webcam opened. Starting...\n")

    frame_count     = 0
    fps_time        = time.time()
    ocr_thread      = None
    last_detections = []

    # Flag to pause alerts during scene description
    scene_mode = [False]

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame_count  += 1
        frame_height  = frame.shape[0]
        frame_width   = frame.shape[1]

        # Step 1: Object Detection
        detections = detector.detect(frame)

        # Step 2: Distance Estimation
        # Vehicles → real meters  |  Others → original zone
        detections = estimator.estimate_all(detections, frame_height=frame_height)
        last_detections = detections

        # Step 3: OCR in background thread
        if frame_count % OCR_FRAME_INTERVAL == 0:
            if ocr_thread is None or not ocr_thread.is_alive():
                ocr_thread = threading.Thread(
                    target=ocr_worker,
                    args=(ocr, frame.copy(), ocr_result),
                    daemon=True
                )
                ocr_thread.start()

        with ocr_result["lock"]:
            ocr_text = ocr_result["text"]
            ocr_result["text"] = ""

        if ocr_text:
            print(f"[OCR] Detected text: {ocr_text}")

        # Step 4: Context + Direction
        # Skip normal alerts during scene description
        if not scene_mode[0]:
            alerts = context.generate_alerts(
                detections,
                ocr_text=ocr_text,
                frame_width=frame_width
            )

            if alerts:
                for alert in alerts:
                    print(f"[Alert] {alert}")
                ocr_alerts   = [a for a in alerts if "Sign" in a or "அடையாளம்" in a]
                other_alerts = [a for a in alerts if "Sign" not in a and "அடையாளம்" not in a]
                speaker[0].speak_all(ocr_alerts)
                speaker[0].speak_all(other_alerts)

        # Step 5: Draw detections
        annotated_frame = detector.draw_boxes(frame, detections)

        for det in detections:
            x1, y1, x2, y2 = det["bbox"]
            zone   = det.get("distance_zone", "")
            dist_m = det.get("distance_m")          # NEW — meters for vehicles
            cx     = (x1 + x2) // 2
            ratio  = cx / frame_width
            if ratio < 0.33:
                dir_label = "LEFT"
            elif ratio < 0.66:
                dir_label = "CENTRE"
            else:
                dir_label = "RIGHT"

            zone_color = {"SAFE": (0,255,0), "CAUTION": (0,165,255), "DANGER": (0,0,255)}
            color = zone_color.get(zone, (255,255,255))

            # NEW — show "DANGER 1.4m LEFT" for vehicles, "DANGER LEFT" for others
            if dist_m is not None:
                label_text = f"{zone} {dist_m}m {dir_label}"
            else:
                label_text = f"{zone} {dir_label}"

            cv2.putText(annotated_frame, label_text, (x1, y2+20),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.45, color, 2)

        elapsed = time.time() - fps_time
        fps = frame_count / elapsed if elapsed > 0 else 0
        cv2.putText(annotated_frame, f"FPS: {fps:.1f}", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255,255,0), 2)

        lang_label = "EN" if current_language[0] == "english" else "TA"
        lang_color = (0,255,0) if current_language[0] == "english" else (0,165,255)
        cv2.putText(annotated_frame, f"Lang: {lang_label}", (10, 58),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, lang_color, 2)

        if ocr_text:
            cv2.putText(annotated_frame, f"Text: {ocr_text[:40]}", (10, frame_height-20),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255,255,0), 2)

        cv2.imshow(WINDOW_NAME, annotated_frame)

        key = cv2.waitKey(1) & 0xFF

        if key == ord('q'):
            print("\n[Main] Q pressed. Shutting down...")
            break

        elif key == ord('s'):
            # Stop all pending alerts first, then speak scene
            print("\n[Main] S pressed — describing scene...")
            scene_mode[0] = True
            speaker[0].stop()
            time.sleep(0.5)
            speaker[0] = make_speaker(current_language[0])
            sos.update_speaker(speaker[0], current_language[0])      # NEW
            places.update_speaker(speaker[0], current_language[0])   # NEW
            description = context.describe_scene(last_detections, frame_width=frame_width)
            print(f"[Scene] {description}")
            speaker[0].speak(description)
            time.sleep(3)
            scene_mode[0] = False

        elif key == ord('e') and current_language[0] != "english":
            print("\n[Main] Switched to ENGLISH")
            speaker[0].stop()
            time.sleep(1)
            current_language[0] = "english"
            context    = ContextEngine(cooldown=5, language="english")
            speaker[0] = make_speaker("english")
            sos.update_speaker(speaker[0], "english")       # NEW
            places.update_speaker(speaker[0], "english")    # NEW
            speaker[0].speak("Switched to English.")

        elif key == ord('t') and current_language[0] != "tamil":
            print("\n[Main] Switched to TAMIL")
            speaker[0].stop()
            time.sleep(1)
            current_language[0] = "tamil"
            context    = ContextEngine(cooldown=5, language="tamil")
            speaker[0] = make_speaker("tamil")
            sos.update_speaker(speaker[0], "tamil")         # NEW
            places.update_speaker(speaker[0], "tamil")      # NEW
            speaker[0].speak("தமிழுக்கு மாறினோம்.")

        elif key == ord('o'):                                # NEW — SOS
            sos.trigger_sos()

        elif key == ord('p'):                                # NEW — Nearby places
            print("[Main] Enter place keyword (hotel/temple/atm/hospital etc): ", end="", flush=True)
            keyword  = input().strip() or "restaurant"
            location = sos.get_location()
            if location:
                places.announce_nearby(location[0], location[1], keyword=keyword)
            else:
                msg = "இடம் கிடைக்கவில்லை." if current_language[0] == "tamil" else "GPS location not available."
                speaker[0].speak(msg)

    cap.release()
    cv2.destroyAllWindows()
    speaker[0].stop()
    print("[Main] VisionGuard stopped. Goodbye.")


if __name__ == "__main__":
    main()
