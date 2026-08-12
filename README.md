# Camera Guardian 🎥

**Motion Detection System powered by Roboflow**

A real-time object detection system that monitors a webcam 24/7 and alerts you when it detects people using Roboflow's computer vision API.

## Features

- ✅ **24/7 Monitoring** - Continuous webcam stream processing
- ✅ **Real-time Detection** - Uses Roboflow's trained object detection model
- ✅ **Smart Alerts** - Prevents spam with configurable cooldown periods
- ✅ **Persistent Storage** - All detections saved to SQLite database
- ✅ **Environment Configuration** - Secrets managed via `.env`
- ✅ **Production-Ready** - Clean code, proper error handling, logging

## Quick Start

### Prerequisites

- Python 3.10+
- Webcam
- Roboflow account (free tier OK)

### Installation

```bash
# Clone the repository
git clone https://github.com/ggbc/camera-guardian.git
cd camera-guardian

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# or: venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt
```

### Configuration

1. **Get your Roboflow API credentials:**
   - Go to https://app.roboflow.com/settings/api
   - Copy your **Private API Key**
   - Go to your project and note the **Project ID** and **Model Version**

2. **Create `.env` file:**
```bash
   cp .env.example .env
```

3. **Edit `.env` with your credentials:**
ROBOFLOW_API_KEY=your_private_key_here
ROBOFLOW_PROJECT_ID=your_project_id
ROBOFLOW_MODEL_VERSION=2
FRAME_INTERVAL=1
ALERT_COOLDOWN=30

### Usage

```bash
python src/main.py
```

Output:

============================================================
🎥 CAMERA GUARDIAN - 24/7 MONITORING
Project: detect-people-wqfy8
Model Version: 2
Frame Interval: 1s
Alert Cooldown: 30s
Monitoring: people

📷 Conectando à câmera 0...
✓ Webcam conectada
🚨 ALERTA: PEOPLE detectado (98.1%)
📍 PEOPLE detectado (98.1%) - cooldown ativo

📊 Status: 20 frames, 13 detecções
• people: 29

Press `Ctrl+C` to stop.

## Testing

Test the Roboflow API integration:

```bash
python tests/test_roboflow.py
```

This will:
1. Try to capture from webcam
2. Fall back to file upload if needed
3. Show detected objects with confidence scores

## Architecture

### Core Modules

**`src/camera.py`** - Webcam capture
- Opens webcam stream
- Captures frames at specified intervals
- Returns JPEG-encoded bytes for API

**`src/detector.py`** - Roboflow integration
- Sends frames to Roboflow API
- Parses detection results
- Filters by class and confidence threshold

**`src/storage.py`** - Persistent storage
- SQLite database for detection history
- Query recent detections
- Compute statistics

**`src/main.py`** - Orchestration
- Main monitoring loop
- Coordinates camera capture, detection, storage
- Handles alerts with cooldown logic

### Data Flow
Webcam
↓
[WebcamCapture] - Frame extraction every N seconds
↓
[Roboflow API] - Object detection inference
↓
[Detection Filter] - Class & confidence threshold
↓
[Database] - Persistent storage
↓
[Alert Logic] - Cooldown + notification

## Configuration Reference

| Variable | Default | Description |
|----------|---------|-------------|
| `ROBOFLOW_API_KEY` | — | Private API key from Roboflow |
| `ROBOFLOW_PROJECT_ID` | — | Project ID in Roboflow workspace |
| `ROBOFLOW_MODEL_VERSION` | 2 | Model version to use |
| `FRAME_INTERVAL` | 1 | Seconds between frame captures |
| `ALERT_COOLDOWN` | 30 | Seconds before re-alerting for same class |

## Database

Detections are stored in `./data/detections.db` (SQLite).

### Schema

```sql
CREATE TABLE detections (
    id INTEGER PRIMARY KEY,
    class_name TEXT NOT NULL,
    confidence REAL NOT NULL,
    timestamp TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Query Examples

```python
from src.storage import Database

db = Database()

# Get recent detections
recent = db.get_recent(limit=20)

# Get statistics
stats = db.get_stats()
print(stats)
# Output: {'total': 42, 'by_class': {'people': 42}}
```

## Roadmap

- [ ] Email alerts
- [ ] SMS alerts (Twilio)
- [ ] Web dashboard
- [ ] Multiple camera support
- [ ] Custom model training
- [ ] Webhook integration
- [ ] Docker deployment

## Development

### Running Tests

```bash
python tests/test_roboflow.py
```

### Project Structure
camera-guardian/
├── src/
│ ├── main.py # Entry point
│ ├── camera.py # Webcam capture
│ ├── detector.py # Roboflow API client
│ └── storage.py # SQLite database
├── tests/
│ ├── test_roboflow.py # API integration tests
├── data/
│ └── detections.db # SQLite database (created at runtime)
├── .env # Environment variables (DO NOT COMMIT)
├── .env.example # Example configuration
├── requirements.txt # Python dependencies
└── README.md # This file

## Troubleshooting

### "Unauthorized api_key" Error

Make sure you're using the **Private API Key**, not the Publishable one.

### "0 detections" even with people visible

- Check webcam quality (lighting, focus)
- Lower the confidence threshold in `main.py`
- Verify model is trained and published on Roboflow

### Webcam not opening

- Check device permissions: `ls -la /dev/video0`
- Try different camera index: edit `WebcamCapture(camera_index=1)`

## Security

⚠️ **IMPORTANT**: Never commit `.env` file to version control!

- `.env` is in `.gitignore` by default
- Use `.env.example` for reference
- Store secrets in environment variables, not code

## License

MIT License - See LICENSE file for details

## Contributing

Built as part of a portfolio project demonstrating:
- Real-time computer vision integration
- Clean Python architecture
- API client development
- Database design
- Error handling & logging

---
