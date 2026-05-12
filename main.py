"""
main.py - VisionGuard: AI-Based Context-Aware Smart Assistive System
----------------------------------------------------------------------
Controls:
  E = English voice
  T = Tamil voice
  S = Scene description
  O = SOS emergency alert
  P = Current place announcement
  Q = Quit
"""

import cv2
import time
import threading

from object_detection import ObjectDetector
from distance_estimation import DistanceEstimator
from ocr_module import OCRModule
from context_engine import ContextEngine
from audio_output import AudioOutput
from sos_module import SOSModule
from nearby_places import NearbyPlaces


# ===================================================
YOLO_MODEL = "yolov8n.pt"
CONFIDENCE_THRESHOLD = 0.5
TTS_LANGUAGE = "english"
OCR_FRAME_INTERVAL = 5
WEBCAM_INDEX = 0
WINDOW_NAME = "VisionGuard | E=English T=Tamil S=Scene O=SOS P=Place Q=Quit"
# ===================================================

ocr_result = {"text": "", "lock": threading.Lock()}


def ocr_worker(ocr_module, frame, result_store):
    text = ocr_module.extract_text(frame)
    with result_store["lock"]:
        result_store["text"] = text


def make_speaker(language):
    return AudioOutput(language=language)


def main():
    print("=" * 52)
    print("   VisionGuard: Assistive Vision System")
    print("=" * 52)
    print("   E=English | T=Tamil | S=Scene | O=SOS | P=Place | Q=Quit")
    print("=" * 52)

    print("\n[Main] Initializing modules...")

    detector = ObjectDetector(
        model_path=YOLO_MODEL,
        confidence_threshold=CONFIDENCE_THRESHOLD
    )

    estimator = DistanceEstimator()
    ocr = OCRModule(language="eng")

    current_language = [TTS_LANGUAGE]
    context = ContextEngine(cooldown=5, language=current_language[0])

    speaker = [make_speaker(current_language[0])]

    sos = SOSModule(
        speaker=speaker[0],
        language=current_language[0],
        simulate=True
    )

    places = NearbyPlaces(
        speaker=speaker[0],
        language=current_language[0]
    )

    print("[Main] All modules initialized.\n")
    speaker[0].speak("VisionGuard system started. Camera is active.")

    cap = cv2.VideoCapture(WEBCAM_INDEX)

    if not cap.isOpened():
        print("[Main] ERROR: Could not open webcam.")
        return

    print("[Main] Webcam opened. Starting...\n")

    frame_count = 0
    fps_time = time.time()
    ocr_thread = None
    last_detections = []

    scene_mode = [False]

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame_count += 1
        frame_height = frame.shape[0]
        frame_width = frame.shape[1]

        # ---------------------------------------------------
        # Object detection
        # ---------------------------------------------------
        detections = detector.detect(frame)
        detections = estimator.estimate_all(
            detections,
            frame_height=frame_height
        )

        last_detections = detections

        # ---------------------------------------------------
        # OCR
        # ---------------------------------------------------
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

        # ---------------------------------------------------
        # Alerts
        # ---------------------------------------------------
        if not scene_mode[0]:
            alerts = context.generate_alerts(
                detections,
                ocr_text=ocr_text,
                frame_width=frame_width
            )

            if alerts:
                for alert in alerts:
                    print(f"[Alert] {alert}")
                speaker[0].speak_all(alerts)

        # ---------------------------------------------------
        # Draw boxes
        # ---------------------------------------------------
        annotated_frame = detector.draw_boxes(frame, detections)

        elapsed = time.time() - fps_time
        fps = frame_count / elapsed if elapsed > 0 else 0

        cv2.putText(
            annotated_frame,
            f"FPS: {fps:.1f}",
            (10, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255, 255, 0),
            2
        )

        lang_label = "EN" if current_language[0] == "english" else "TA"

        cv2.putText(
            annotated_frame,
            f"Lang: {lang_label}",
            (10, 60),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0, 255, 0),
            2
        )

        cv2.imshow(WINDOW_NAME, annotated_frame)

        key = cv2.waitKey(1) & 0xFF

        # ---------------------------------------------------
        # Quit
        # ---------------------------------------------------
        if key == ord("q"):
            print("\n[Main] Q pressed. Shutting down...")
            break

        # ---------------------------------------------------
        # Scene description
        # ---------------------------------------------------
        elif key == ord("s"):
            print("\n[Main] S pressed - describing scene...")

            scene_mode[0] = True
            speaker[0].stop()
            time.sleep(0.5)

            speaker[0] = make_speaker(current_language[0])
            sos.update_speaker(speaker[0], current_language[0])
            places.update_speaker(speaker[0], current_language[0])

            description = context.describe_scene(
                last_detections,
                frame_width=frame_width
            )

            print(f"[Scene] {description}")
            speaker[0].speak(description)

            time.sleep(3)
            scene_mode[0] = False

        # ---------------------------------------------------
        # English
        # ---------------------------------------------------
        elif key == ord("e") and current_language[0] != "english":
            print("\n[Main] Switched to ENGLISH")

            speaker[0].stop()
            time.sleep(1)

            current_language[0] = "english"
            context = ContextEngine(cooldown=5, language="english")
            speaker[0] = make_speaker("english")

            sos.update_speaker(speaker[0], "english")
            places.update_speaker(speaker[0], "english")

            speaker[0].speak("Switched to English.")

        # ---------------------------------------------------
        # Tamil
        # ---------------------------------------------------
        elif key == ord("t") and current_language[0] != "tamil":
            print("\n[Main] Switched to TAMIL")

            speaker[0].stop()
            time.sleep(1)

            current_language[0] = "tamil"
            context = ContextEngine(cooldown=5, language="tamil")
            speaker[0] = make_speaker("tamil")

            sos.update_speaker(speaker[0], "tamil")
            places.update_speaker(speaker[0], "tamil")

            speaker[0].speak("தமிழுக்கு மாறினோம்.")

        # ---------------------------------------------------
        # SOS
        # ---------------------------------------------------
        elif key == ord("o"):
            sos.trigger_sos()

        # ---------------------------------------------------
        # Current place
        # ---------------------------------------------------
        elif key == ord('p'):
            print("[Main] P pressed - finding nearest hospital...")

            location = sos.get_location()

            if location:
                places.announce_nearby(location[0], location[1])
            else:
                speaker[0].speak("Unable to detect current location")
    cap.release()
    cv2.destroyAllWindows()
    speaker[0].stop()
    print("[Main] VisionGuard stopped. Goodbye.")


if __name__ == "__main__":
    main()
