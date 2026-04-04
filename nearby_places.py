"""
nearby_places.py - VisionGuard Nearby Places Module
-----------------------------------------------------
Press 'P' key → type keyword in terminal → announces nearby places via TTS.

Supported keywords:
  hotel, restaurant, temple, church, mosque, hospital,
  pharmacy, atm, bank, bus, shop, park, school, police

Requires:
  1. Google Places API key — get free at https://console.cloud.google.com
  2. Internet connection
"""

import requests

# ============================================================
# PASTE YOUR GOOGLE PLACES API KEY HERE
# ============================================================
GOOGLE_API_KEY = "YOUR_GOOGLE_PLACES_API_KEY_HERE"
# ============================================================

SEARCH_RADIUS_M = 500
MAX_RESULTS     = 3

KEYWORD_TO_TYPE = {
    "hotel":      "lodging",      "hotels":     "lodging",
    "restaurant": "restaurant",   "food":       "restaurant",
    "eat":        "restaurant",   "temple":     "hindu_temple",
    "church":     "church",       "mosque":     "mosque",
    "hospital":   "hospital",     "pharmacy":   "pharmacy",
    "medical":    "pharmacy",     "atm":        "atm",
    "bank":       "bank",         "bus":        "bus_station",
    "shop":       "store",        "store":      "store",
    "park":       "park",         "school":     "school",
    "police":     "police",       "toilet":     "toilet",
}

# Tamil translations for place announcements
PLACE_TYPE_TA = {
    "hotel": "ஹோட்டல்", "restaurant": "உணவகம்", "temple": "கோயில்",
    "hospital": "மருத்துவமனை", "atm": "ஏ டி எம்", "bank": "வங்கி",
    "pharmacy": "மருந்தகம்", "bus": "பஸ் நிலையம்", "shop": "கடை",
    "park": "பூங்கா", "school": "பள்ளி", "police": "காவல் நிலையம்",
}


class NearbyPlaces:

    def __init__(self, speaker=None, language="english", api_key=GOOGLE_API_KEY):
        self.speaker  = speaker
        self.language = language
        self.api_key  = api_key

    def update_speaker(self, speaker, language):
        """Call when user switches language."""
        self.speaker  = speaker
        self.language = language

    def announce_nearby(self, latitude, longitude, keyword="restaurant"):
        """Find and speak nearby places. Called from main.py on 'P' key."""

        if self.api_key == "YOUR_GOOGLE_PLACES_API_KEY_HERE":
            print("[NearbyPlaces] No API key set.")
            if self.speaker:
                if self.language == "tamil":
                    self.speaker.speak("அருகிலுள்ள இடங்கள் அமைக்கப்படவில்லை.")
                else:
                    self.speaker.speak("Nearby places feature not configured. Please add API key.")
            return

        place_type = KEYWORD_TO_TYPE.get(keyword.lower().strip())
        if not place_type:
            if self.speaker:
                msg = f"தெரியவில்லை: {keyword}" if self.language == "tamil" else f"Unknown place type: {keyword}"
                self.speaker.speak(msg)
            return

        print(f"[NearbyPlaces] Searching '{keyword}' near ({latitude:.4f}, {longitude:.4f})")

        if self.speaker:
            if self.language == "tamil":
                ta_keyword = PLACE_TYPE_TA.get(keyword.lower(), keyword)
                self.speaker.speak(f"அருகிலுள்ள {ta_keyword} தேடுகிறேன். கொஞ்சம் காத்திருங்கள்.")
            else:
                self.speaker.speak(f"Searching for nearby {keyword}. Please wait.")

        places = self._fetch(latitude, longitude, place_type)

        if not places:
            if self.speaker:
                if self.language == "tamil":
                    self.speaker.speak(f"அருகில் {keyword} எதுவும் இல்லை.")
                else:
                    self.speaker.speak(f"No {keyword} found nearby.")
            return

        if self.language == "tamil":
            ta_keyword = PLACE_TYPE_TA.get(keyword.lower(), keyword)
            announcement = f"{len(places)} {ta_keyword} கண்டறியப்பட்டது. "
            for i, place in enumerate(places, 1):
                dist = f"{place['distance_m']} மீட்டர்" if place["distance_m"] else ""
                announcement += f"எண் {i}: {place['name']}. {dist}. "
        else:
            announcement = f"Found {len(places)} {keyword} nearby. "
            for i, place in enumerate(places, 1):
                dist = f"{place['distance_m']} metres away" if place["distance_m"] else ""
                announcement += f"Number {i}: {place['name']}. {dist}. "

        for i, place in enumerate(places, 1):
            print(f"[NearbyPlaces] {i}. {place['name']} — {place['address']} ({place['distance_m']}m)")

        if self.speaker:
            self.speaker.speak(announcement)

    def _fetch(self, lat, lon, place_type):
        url    = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
        params = {"location": f"{lat},{lon}", "radius": SEARCH_RADIUS_M,
                  "type": place_type, "key": self.api_key}
        try:
            data   = requests.get(url, params=params, timeout=6).json()
            status = data.get("status")
            if status == "ZERO_RESULTS":
                return []
            if status != "OK":
                print(f"[NearbyPlaces] API error: {status}")
                return []
            results = []
            for place in data.get("results", [])[:MAX_RESULTS]:
                loc    = place.get("geometry", {}).get("location", {})
                dist_m = self._haversine(lat, lon, loc.get("lat", lat), loc.get("lng", lon))
                results.append({"name": place.get("name", "Unknown"),
                                 "address": place.get("vicinity", ""),
                                 "distance_m": dist_m})
            return results
        except requests.exceptions.ConnectionError:
            print("[NearbyPlaces] No internet connection.")
            return []
        except Exception as e:
            print(f"[NearbyPlaces] Error: {e}")
            return []

    def _haversine(self, lat1, lon1, lat2, lon2):
        import math
        R  = 6_371_000
        p1, p2 = math.radians(lat1), math.radians(lat2)
        dp, dl = math.radians(lat2-lat1), math.radians(lon2-lon1)
        a  = math.sin(dp/2)**2 + math.cos(p1)*math.cos(p2)*math.sin(dl/2)**2
        return round(2 * R * math.atan2(math.sqrt(a), math.sqrt(1-a)))
