"""
distance_estimation.py - VisionGuard Distance Estimation Module
----------------------------------------------------------------
UPDATED: Vehicles now show real distance in meters.
         All other objects keep the original SAFE/CAUTION/DANGER zone logic.

For VEHICLES (car, truck, bus, motorcycle, bicycle):
    Uses: Distance (m) = (Real Width × Focal Length) / Bounding Box Width
    Gives real distance like "2.3 meters"

For ALL OTHER objects (person, chair, etc.):
    Same as original — SAFE / CAUTION / DANGER based on bounding box height.
"""

# Known real-world widths in meters for vehicles
VEHICLE_REAL_WIDTH_M = {
    "car":        1.8,
    "truck":      2.5,
    "bus":        2.5,
    "motorcycle": 0.7,
    "bicycle":    0.55,
}

FOCAL_LENGTH_PX = 700   # Tune for your camera (default works for 640x480 webcam)

# Vehicle distance thresholds (meters)
VEHICLE_DANGER_M  = 2.0
VEHICLE_CAUTION_M = 6.0

# -------------------------------------------------------
# Original thresholds — unchanged
# -------------------------------------------------------
DANGER_THRESHOLD  = 300
CAUTION_THRESHOLD = 150


class DistanceEstimator:
    """
    Enhanced distance estimator.
    Vehicles  → real meters + zone
    Others    → original zone only (SAFE / CAUTION / DANGER)
    """

    def __init__(self, focal_length=FOCAL_LENGTH_PX):
        self.focal_length = focal_length

    # --------------------------------------------------
    # Original method — kept exactly as before
    # --------------------------------------------------
    def estimate(self, bbox, frame_height=480):
        """
        Original zone estimation using bounding box height ratio.
        Used for non-vehicle objects.
        """
        x1, y1, x2, y2 = bbox
        box_height    = y2 - y1
        relative_size = box_height / frame_height

        if relative_size > 0.6:
            return "DANGER"
        elif relative_size > 0.3:
            return "CAUTION"
        else:
            return "SAFE"

    def get_distance_label(self, zone):
        """Original helper — unchanged."""
        labels = {
            "SAFE":    "far away",
            "CAUTION": "nearby",
            "DANGER":  "very close"
        }
        return labels.get(zone, "unknown distance")

    # --------------------------------------------------
    # NEW: vehicle real distance in meters
    # --------------------------------------------------
    def estimate_vehicle_distance_m(self, label, bbox):
        """
        Returns actual distance in meters for a vehicle.
        Formula: Distance = (Real Width × Focal Length) / Box Width in pixels
        Returns None if not a vehicle.
        """
        real_width = VEHICLE_REAL_WIDTH_M.get(label)
        if real_width is None:
            return None
        x1, y1, x2, y2 = bbox
        box_width_px    = x2 - x1
        if box_width_px <= 0:
            return None
        return round((real_width * self.focal_length) / box_width_px, 1)

    def _zone_from_meters(self, distance_m):
        """Convert vehicle meter distance to zone string."""
        if distance_m <= VEHICLE_DANGER_M:
            return "DANGER"
        elif distance_m <= VEHICLE_CAUTION_M:
            return "CAUTION"
        else:
            return "SAFE"

    # --------------------------------------------------
    # estimate_all — same signature as original
    # --------------------------------------------------
    def estimate_all(self, detections, frame_height=480):
        """
        Adds distance_zone to every detection (same as original).
        Also adds distance_m (meters) for vehicles — None for others.
        """
        for det in detections:
            label = det["label"]
            bbox  = det["bbox"]

            if label in VEHICLE_REAL_WIDTH_M:
                # Vehicle: real meters
                dist_m = self.estimate_vehicle_distance_m(label, bbox)
                det["distance_m"]    = dist_m
                det["distance_zone"] = self._zone_from_meters(dist_m) if dist_m else "SAFE"
            else:
                # Non-vehicle: original zone logic
                det["distance_m"]    = None
                det["distance_zone"] = self.estimate(bbox, frame_height)

        return detections
