class NearbyPlaces:

    def __init__(self, speaker=None, language="english"):
        self.speaker = speaker
        self.language = language

        # Fixed demo data for project presentation
        self.nearest_hospital = "Government Hospital, Shoolagiri"
        self.distance = "7 kilometers"

    def update_speaker(self, speaker, language):
        self.speaker = speaker
        self.language = language

    def announce_nearby(self, latitude=None, longitude=None, keyword="hospital"):
        """
        Press P -> announce nearest hospital only
        """
        try:
            if self.language.lower() == "tamil":
                message = (
                    f"அருகிலுள்ள மருத்துவமனை "
                    f"{self.nearest_hospital}, "
                    f"சுமார் {self.distance} தொலைவில் உள்ளது"
                )
            else:
                message = (
                    f"Nearest hospital is "
                    f"{self.nearest_hospital}, "
                    f"approximately {self.distance} away"
                )

            print(f"[NearbyPlaces] {message}")

            if self.speaker:
                self.speaker.speak(message)

        except Exception as e:
            print("[NearbyPlaces] Error:", e)
