"""
object_detection.py - VisionGuard Object Detection Module
----------------------------------------------------------
Updated by Siri: All 80 YOLO objects included
Grouped by navigation relevance for visually impaired users
"""

from ultralytics import YOLO
import cv2

# -------------------------------------------------------
# All 80 YOLO classes — relevant for visually impaired
# -------------------------------------------------------
RELEVANT_CLASSES = [
    # People
    "person",

    # Vehicles — highest danger
    "car", "truck", "bus", "motorcycle", "bicycle",
    "train", "boat", "airplane",

    # Road signs
    "traffic light", "fire hydrant", "stop sign", "parking meter",

    # Furniture — obstacle risk indoors
    "chair", "couch", "bed", "dining table", "toilet", "bench",

    # Electronics
    "tv", "laptop", "mouse", "remote", "keyboard",
    "cell phone", "microwave", "oven", "toaster", "refrigerator",

    # Kitchen
    "bottle", "wine glass", "cup", "fork", "knife",
    "spoon", "bowl", "sink",

    # Food
    "banana", "apple", "sandwich", "orange", "broccoli",
    "carrot", "hot dog", "pizza", "donut", "cake",

    # Animals — alert needed
    "cat", "dog", "horse", "sheep", "cow",
    "elephant", "bear", "zebra", "giraffe", "bird",

    # Accessories
    "backpack", "umbrella", "handbag", "tie", "suitcase",

    # Sports
    "frisbee", "skis", "snowboard", "sports ball", "kite",
    "baseball bat", "baseball glove", "skateboard",
    "surfboard", "tennis racket",

    # Outdoor / Home
    "potted plant", "vase", "clock", "book",
    "scissors", "teddy bear", "hair drier", "toothbrush",
]


class ObjectDetector:

    def __init__(self, model_path="yolov8n.pt", confidence_threshold=0.5):
        print(f"[ObjectDetector] Loading YOLO model from: {model_path}")
        self.model = YOLO(model_path)
        self.confidence_threshold = confidence_threshold
        print("[ObjectDetector] Model loaded successfully.")

    def detect(self, frame):
        results = self.model(frame, verbose=False)[0]
        detections = []

        for box in results.boxes:
            confidence = float(box.conf[0])
            if confidence < self.confidence_threshold:
                continue

            class_id = int(box.cls[0])
            label = self.model.names[class_id]

            if label not in RELEVANT_CLASSES:
                continue

            x1, y1, x2, y2 = map(int, box.xyxy[0])
            detections.append({
                "label": label,
                "confidence": confidence,
                "bbox": (x1, y1, x2, y2)
            })

        return detections

    def draw_boxes(self, frame, detections):
        for det in detections:
            label = det["label"]
            conf = det["confidence"]
            x1, y1, x2, y2 = det["bbox"]
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            text = f"{label} {conf:.2f}"
            cv2.putText(frame, text, (x1, y1 - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        return frame