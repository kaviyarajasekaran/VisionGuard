"""
context_engine.py - VisionGuard Context-Aware Reasoning Module
---------------------------------------------------------------
Updated by Siri:
  - Added direction detection (left / centre / right)
  - Added scene description (press S key)
  - All 80 YOLO objects in English and Tamil
"""

import time

# -------------------------------------------------------
# English alert templates
# -------------------------------------------------------
ALERT_TEMPLATES_EN = {
    "person":           "Person detected {direction}, {zone}.",
    "car":              "Warning: Car on your {direction}, {zone}.",
    "truck":            "Warning: Truck on your {direction}, {zone}.",
    "bus":              "Warning: Bus on your {direction}, {zone}.",
    "motorcycle":       "Warning: Motorcycle on your {direction}, {zone}.",
    "bicycle":          "Bicycle on your {direction}, {zone}.",
    "train":            "Warning: Train on your {direction}, {zone}.",
    "boat":             "Boat on your {direction}, {zone}.",
    "airplane":         "Airplane on your {direction}, {zone}.",
    "traffic light":    "Traffic light on your {direction}, {zone}.",
    "fire hydrant":     "Fire hydrant on your {direction}, {zone}.",
    "stop sign":        "Stop sign on your {direction}.",
    "parking meter":    "Parking meter on your {direction}, {zone}.",
    "chair":            "Caution: Chair on your {direction}, {zone}.",
    "couch":            "Caution: Couch on your {direction}, {zone}.",
    "bed":              "Caution: Bed on your {direction}, {zone}.",
    "dining table":     "Caution: Table on your {direction}, {zone}.",
    "toilet":           "Toilet on your {direction}, {zone}.",
    "bench":            "Caution: Bench on your {direction}, {zone}.",
    "tv":               "Television on your {direction}, {zone}.",
    "laptop":           "Laptop on your {direction}, {zone}.",
    "mouse":            "Mouse on your {direction}, {zone}.",
    "remote":           "Remote on your {direction}, {zone}.",
    "keyboard":         "Keyboard on your {direction}, {zone}.",
    "cell phone":       "Cell phone on your {direction}, {zone}.",
    "microwave":        "Microwave on your {direction}, {zone}.",
    "oven":             "Oven on your {direction}, {zone}.",
    "toaster":          "Toaster on your {direction}, {zone}.",
    "refrigerator":     "Refrigerator on your {direction}, {zone}.",
    "bottle":           "Bottle on your {direction}, {zone}.",
    "wine glass":       "Glass on your {direction}, {zone}.",
    "cup":              "Cup on your {direction}, {zone}.",
    "fork":             "Fork on your {direction}, {zone}.",
    "knife":            "Caution: Knife on your {direction}, {zone}.",
    "spoon":            "Spoon on your {direction}, {zone}.",
    "bowl":             "Bowl on your {direction}, {zone}.",
    "banana":           "Banana on your {direction}, {zone}.",
    "apple":            "Apple on your {direction}, {zone}.",
    "sandwich":         "Sandwich on your {direction}, {zone}.",
    "orange":           "Orange on your {direction}, {zone}.",
    "broccoli":         "Broccoli on your {direction}, {zone}.",
    "carrot":           "Carrot on your {direction}, {zone}.",
    "hot dog":          "Hot dog on your {direction}, {zone}.",
    "pizza":            "Pizza on your {direction}, {zone}.",
    "donut":            "Donut on your {direction}, {zone}.",
    "cake":             "Cake on your {direction}, {zone}.",
    "cat":              "Cat on your {direction}, {zone}.",
    "dog":              "Dog on your {direction}, {zone}.",
    "horse":            "Caution: Horse on your {direction}, {zone}.",
    "sheep":            "Sheep on your {direction}, {zone}.",
    "cow":              "Caution: Cow on your {direction}, {zone}.",
    "elephant":         "Warning: Elephant on your {direction}, {zone}.",
    "bear":             "Warning: Bear on your {direction}, {zone}.",
    "zebra":            "Zebra on your {direction}, {zone}.",
    "giraffe":          "Giraffe on your {direction}, {zone}.",
    "bird":             "Bird on your {direction}, {zone}.",
    "backpack":         "Backpack on your {direction}, {zone}.",
    "umbrella":         "Umbrella on your {direction}, {zone}.",
    "handbag":          "Handbag on your {direction}, {zone}.",
    "tie":              "Tie on your {direction}, {zone}.",
    "suitcase":         "Suitcase on your {direction}, {zone}.",
    "frisbee":          "Frisbee on your {direction}, {zone}.",
    "skis":             "Skis on your {direction}, {zone}.",
    "snowboard":        "Snowboard on your {direction}, {zone}.",
    "sports ball":      "Ball on your {direction}, {zone}.",
    "kite":             "Kite on your {direction}, {zone}.",
    "baseball bat":     "Caution: Baseball bat on your {direction}, {zone}.",
    "baseball glove":   "Baseball glove on your {direction}, {zone}.",
    "skateboard":       "Caution: Skateboard on your {direction}, {zone}.",
    "surfboard":        "Surfboard on your {direction}, {zone}.",
    "tennis racket":    "Tennis racket on your {direction}, {zone}.",
    "potted plant":     "Plant on your {direction}, {zone}.",
    "vase":             "Caution: Vase on your {direction}, {zone}.",
    "clock":            "Clock on your {direction}, {zone}.",
    "book":             "Book on your {direction}, {zone}.",
    "scissors":         "Caution: Scissors on your {direction}, {zone}.",
    "teddy bear":       "Teddy bear on your {direction}, {zone}.",
    "hair drier":       "Hair drier on your {direction}, {zone}.",
    "toothbrush":       "Toothbrush on your {direction}, {zone}.",
    "sink":             "Sink on your {direction}, {zone}.",
}

# -------------------------------------------------------
# Tamil alert templates
# -------------------------------------------------------
ALERT_TEMPLATES_TA = {
    "person":           "நபர் உங்கள் {direction} பக்கம், {zone}.",
    "car":              "எச்சரிக்கை: கார் உங்கள் {direction} பக்கம், {zone}.",
    "truck":            "எச்சரிக்கை: லாரி உங்கள் {direction} பக்கம், {zone}.",
    "bus":              "எச்சரிக்கை: பேருந்து உங்கள் {direction} பக்கம், {zone}.",
    "motorcycle":       "எச்சரிக்கை: மோட்டார் சைக்கிள் உங்கள் {direction} பக்கம், {zone}.",
    "bicycle":          "சைக்கிள் உங்கள் {direction} பக்கம், {zone}.",
    "train":            "எச்சரிக்கை: ரயில் உங்கள் {direction} பக்கம், {zone}.",
    "boat":             "படகு உங்கள் {direction} பக்கம், {zone}.",
    "airplane":         "விமானம் உங்கள் {direction} பக்கம், {zone}.",
    "traffic light":    "போக்குவரத்து விளக்கு உங்கள் {direction} பக்கம், {zone}.",
    "fire hydrant":     "தீ குழாய் உங்கள் {direction} பக்கம், {zone}.",
    "stop sign":        "நிறுத்த அடையாளம் உங்கள் {direction} பக்கம்.",
    "parking meter":    "பார்க்கிங் மீட்டர் உங்கள் {direction} பக்கம், {zone}.",
    "chair":            "கவனம்: நாற்காலி உங்கள் {direction} பக்கம், {zone}.",
    "couch":            "கவனம்: சோபா உங்கள் {direction} பக்கம், {zone}.",
    "bed":              "கவனம்: படுக்கை உங்கள் {direction} பக்கம், {zone}.",
    "dining table":     "கவனம்: மேசை உங்கள் {direction} பக்கம், {zone}.",
    "toilet":           "கழிவறை உங்கள் {direction} பக்கம், {zone}.",
    "bench":            "கவனம்: பெஞ்ச் உங்கள் {direction} பக்கம், {zone}.",
    "tv":               "தொலைக்காட்சி உங்கள் {direction} பக்கம், {zone}.",
    "laptop":           "லேப்டாப் உங்கள் {direction} பக்கம், {zone}.",
    "cell phone":       "செல்போன் உங்கள் {direction} பக்கம், {zone}.",
    "refrigerator":     "குளிர்சாதனப்பெட்டி உங்கள் {direction} பக்கம், {zone}.",
    "bottle":           "பாட்டில் உங்கள் {direction} பக்கம், {zone}.",
    "knife":            "கவனம்: கத்தி உங்கள் {direction} பக்கம், {zone}.",
    "cat":              "பூனை உங்கள் {direction} பக்கம், {zone}.",
    "dog":              "நாய் உங்கள் {direction} பக்கம், {zone}.",
    "cow":              "கவனம்: மாடு உங்கள் {direction} பக்கம், {zone}.",
    "elephant":         "எச்சரிக்கை: யானை உங்கள் {direction} பக்கம், {zone}.",
    "bear":             "எச்சரிக்கை: கரடி உங்கள் {direction} பக்கம், {zone}.",
    "bird":             "பறவை உங்கள் {direction} பக்கம், {zone}.",
    "backpack":         "பேக்பேக் உங்கள் {direction} பக்கம், {zone}.",
    "suitcase":         "சூட்கேஸ் உங்கள் {direction} பக்கம், {zone}.",
    "sports ball":      "பந்து உங்கள் {direction} பக்கம், {zone}.",
    "scissors":         "கவனம்: கத்தரிக்கோல் உங்கள் {direction} பக்கம், {zone}.",
}

# Zone phrases
ZONE_PHRASES_EN = {
    "SAFE":    "in the distance",
    "CAUTION": "nearby",
    "DANGER":  "very close — please stop"
}

ZONE_PHRASES_TA = {
    "SAFE":    "தூரத்தில்",
    "CAUTION": "அருகில்",
    "DANGER":  "மிகவும் அருகில் — நிறுத்துங்கள்"
}

# Direction phrases
DIRECTION_EN = {
    "left":   "left",
    "centre": "centre",
    "right":  "right"
}

DIRECTION_TA = {
    "left":   "இடது",
    "centre": "நடு",
    "right":  "வலது"
}

ALERT_COOLDOWN_SECONDS = 5


class ContextEngine:

    def __init__(self, cooldown=ALERT_COOLDOWN_SECONDS, language="english"):
        self.cooldown = cooldown
        self.language = language.lower()
        self.last_alert_time = {}

        if self.language == "tamil":
            self.templates  = ALERT_TEMPLATES_TA
            self.zone_phrases = ZONE_PHRASES_TA
            self.directions = DIRECTION_TA
        else:
            self.templates  = ALERT_TEMPLATES_EN
            self.zone_phrases = ZONE_PHRASES_EN
            self.directions = DIRECTION_EN

    def _can_alert(self, key):
        now = time.time()
        last = self.last_alert_time.get(key, 0)
        if now - last >= self.cooldown:
            self.last_alert_time[key] = now
            return True
        return False

    def _get_direction(self, bbox, frame_width=640):
        """
        Detect object direction based on bounding box centre.
        Frame divided into 3 equal zones: left / centre / right
        """
        x1, y1, x2, y2 = bbox
        centre_x = (x1 + x2) / 2
        ratio = centre_x / frame_width

        if ratio < 0.33:
            return "left"
        elif ratio < 0.66:
            return "centre"
        else:
            return "right"

    def generate_alerts(self, detections, ocr_text="", frame_width=640):
        alerts = []

        priority_order = {"DANGER": 0, "CAUTION": 1, "SAFE": 2}
        sorted_detections = sorted(
            detections,
            key=lambda d: priority_order.get(d.get("distance_zone", "SAFE"), 2)
        )

        for det in sorted_detections:
            label     = det.get("label", "object")
            zone      = det.get("distance_zone", "SAFE")
            bbox      = det.get("bbox", (0, 0, 100, 100))
            zone_phrase = self.zone_phrases.get(zone, "")

            # Get direction
            raw_dir   = self._get_direction(bbox, frame_width)
            direction = self.directions.get(raw_dir, raw_dir)

            alert_key = f"{label}_{zone}_{raw_dir}"
            if not self._can_alert(alert_key):
                continue

            template = self.templates.get(
                label,
                f"{label} உங்கள் {{direction}} பக்கம், {{zone}}." if self.language == "tamil"
                else f"{label} on your {{direction}}, {{zone}}."
            )
            
            message = template.format(direction=direction, zone=zone_phrase)

            # Add real distance in meters for vehicles
            dist_m = det.get("distance_m")
            if dist_m is not None:
                if self.language == "tamil":
                    message = message.rstrip(".") + f". தூரம் {dist_m} மீட்டர்."
                else:
                    message = message.rstrip(".") + f". Distance: {dist_m} meters."

            if zone == "DANGER":
                prefix = "ஆபத்து! " if self.language == "tamil" else "Danger! "
                message = prefix + message

            alerts.append(message)

        # OCR alert
        if ocr_text and len(ocr_text.strip()) >= 3:
            ocr_key = f"ocr_{ocr_text[:20]}"
            if self._can_alert(ocr_key):
                if self.language == "tamil":
                    alerts.append(f"அடையாளம் கண்டறியப்பட்டது: {ocr_text.strip()}")
                else:
                    alerts.append(f"Sign detected: {ocr_text.strip()}")

        return alerts

    def describe_scene(self, detections, frame_width=640):
        """
        Generate full scene description.
        Called when user presses S key.
        """
        if not detections:
            return "No objects detected nearby." if self.language == "english" else "அருகில் பொருட்கள் இல்லை."

        # Count objects
        label_counts = {}
        for det in detections:
            label = det["label"]
            label_counts[label] = label_counts.get(label, 0) + 1

        # Build description
        parts = []
        for label, count in label_counts.items():
            if count == 1:
                # Get direction for single objects
                det = next(d for d in detections if d["label"] == label)
                raw_dir  = self._get_direction(det["bbox"], frame_width)
                direction = self.directions.get(raw_dir, raw_dir)
                if self.language == "tamil":
                    parts.append(f"ஒரு {label} உங்கள் {direction} பக்கம்")
                else:
                    parts.append(f"one {label} on your {direction}")
            else:
                if self.language == "tamil":
                    parts.append(f"{count} {label}")
                else:
                    parts.append(f"{count} {label}s")

        if self.language == "tamil":
            return "முன்னால் " + ", ".join(parts) + " உள்ளது."
        else:
            return "I can see " + ", ".join(parts) + " ahead."