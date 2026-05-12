# VisionGuard 👁️ — AI Based Context-Aware Smart Assistive System

An AI-powered assistive vision system designed for visually impaired individuals.  
VisionGuard detects surrounding objects, estimates distance, reads text, provides scene understanding, and triggers emergency alerts with voice assistance in both English and Tamil.

---

## Features

- Real-time object detection using YOLOv8
- Distance estimation with safety zones:
  - SAFE
  - CAUTION
  - DANGER
- Direction detection:
  - LEFT
  - CENTRE
  - RIGHT
- OCR text reading using EasyOCR
- Priority-based voice alerts (danger alerts first)
- Bilingual voice support:
  - English (offline)
  - Tamil (online)
- Live language switching during runtime
- Scene description on demand
- SOS emergency alert system
- WhatsApp SOS alert with Google Maps location
- Demo mode with fixed college location
- Nearby hospital detection from current/demo location
- Alert logging in TXT format

---

## Controls

| Key | Action |
|-----|--------|
| E | Switch to English voice |
| T | Switch to Tamil voice |
| S | Describe current scene |
| O | Trigger SOS emergency alert |
| P | Announce nearby hospital |
| Q | Quit application |

---

## SOS Emergency Feature

When **O** is pressed:

- Emergency voice alert is triggered
- SOS message is generated automatically
- WhatsApp opens and sends alert message
- Google Maps location link is included
- SOS event is logged into `sos_log.txt`

### Demo Mode
For project presentation, VisionGuard uses a fixed demo location:

**Er. Perumal Manimekalai College of Engineering, Koneripalli**

This ensures consistent testing during project demonstration.

---

## Nearby Hospital Feature

When **P** is pressed:

- VisionGuard identifies the current/demo location
- Announces nearest hospital/clinic near the college location
- Voice output available in English and Tamil

Example:
- Government Hospital, Shoolagiri
- Nearby local clinics around Koneripalli

---

## Installation

```bash
pip install -r requirements.txt
python main.py
```

---

## Project Files

| File | Purpose |
|------|---------|
| main.py | Main execution file |
| object_detection.py | YOLOv8 object detection |
| distance_estimation.py | Distance zone estimation |
| ocr_module.py | OCR text extraction |
| context_engine.py | Context-aware alerts & scene description |
| audio_output.py | English/Tamil voice output |
| sos_module.py | SOS emergency alert system |
| nearby_places.py | Nearby hospital/location module |

---

## Future Enhancements

- Raspberry Pi wearable integration
- Smart glasses camera module
- GPS hardware integration
- GSM emergency calling
- Fully offline Tamil voice support
- Live hospital search with internet API

---

## References

1. Raskar, A. (2025). *Visual Recognition Based Mobile Application for Visually Impaired People*  
2. Samad, M. (2024). *AI Based Wearable Vision Assistance System for Visually Impaired People*

---

## Authors

| Name | Role |
|------|------|
| Kaviya R | Object Detection & System Integration |
| Veena R | OCR & Text Recognition |
| Maheswari R | Voice Output & SOS Module |

---

## Project Information

**Final Year Project**  
**Title:** AI Based Context-Aware Smart Assistive System for Visually Impaired People
