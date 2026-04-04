# VisionGuard 👁️ — AI Based Assistive Vision System

An AI-powered wearable vision assistance system for visually impaired people.
Detects objects, reads text, estimates distance, and gives voice alerts in English and Tamil.

---

## Features

- Real-time object detection (80 objects) using YOLOv8
- Distance estimation — SAFE / CAUTION / DANGER zones
- Direction detection — LEFT / CENTRE / RIGHT
- OCR text reading using EasyOCR
- Priority-based voice alerts — danger first
- Bilingual support — English (offline) + Tamil (online)
- Live language switching during runtime
- Scene description on demand
- SOS emergency alert with voice + notification
- Alert logging to CSV and TXT

---

## Controls

| Key | Action |
|-----|--------|
| E | Switch to English voice |
| T | Switch to Tamil voice |
| S | Describe current scene |
| SPACE | SOS Emergency Alert |
| Q | Quit |

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
| main.py | Main entry point |
| object_detection.py | YOLOv8 detection module |
| distance_estimation.py | Distance zone estimation |
| ocr_module.py | EasyOCR text reading |
| context_engine.py | Alert generation + direction |
| audio_output.py | Voice output English + Tamil |
| sos_module.py | SOS emergency module |
| alert_logger.py | Detection logging to file |

---

## Hardware Phase (Coming Soon)

- Raspberry Pi 5 + Camera glasses
- Bluetooth headphones
- Direct emergency calling (108 / 100)
- GPS location sharing
- Offline Tamil voice

---

## References

- Raskar, A. (2025). Visual Recognition Based Mobile Application for Visually Impaired People
- Samad, M. (2024). AI Based Wearable Vision Assistance System for Visually Impaired People

---

## Authors

| Name | Role |
|------|------|
| Kaviya R | Object Detection & System Integration |
| Veena R | OCR & Text Recognition |
| Maheswari R | Voice Output & SOS Module |

---

## Project

Final Year Project — AI Based Assistive Vision System for Visually Impaired People
