# Sign Language to Text Conversion App

A real-time sign language to text conversion application with:
- **Backend**: Python Django REST API with WebSocket support
- **Frontend**: Flutter mobile/web app

## Project Structure

```
sign_to_text_flutter/
├── backend/                 # Django REST API
│   ├── manage.py
│   ├── requirements.txt
│   ├── sign_language_api/   # Django project settings
│   │   ├── settings.py
│   │   ├── urls.py
│   │   ├── asgi.py         # WebSocket support
│   │   └── wsgi.py
│   └── gestures/           # Main app
│       ├── models.py       # Database models
│       ├── views.py        # API endpoints
│       ├── serializers.py  # REST serializers
│       ├── sign_detector.py # Sign detection logic
│       ├── consumers.py    # WebSocket consumers
│       └── routing.py      # WebSocket routing
│
├── frontend/               # Flutter app
│   ├── lib/
│   │   ├── main.dart
│   │   ├── models/         # Data models
│   │   ├── providers/      # State management
│   │   ├── screens/        # UI screens
│   │   ├── services/       # API services
│   │   └── widgets/        # Reusable widgets
│   └── pubspec.yaml
│
└── venv/                   # Python virtual environment
```

## Setup Instructions

### Backend (Django)

1. **Activate virtual environment**:
   ```powershell
   cd sign_to_text_flutter
   .\venv\Scripts\activate
   ```

2. **Install dependencies**:
   ```powershell
   cd backend
   pip install -r requirements.txt
   ```

3. **Run migrations**:
   ```powershell
   python manage.py migrate
   ```

4. **Create superuser (optional)**:
   ```powershell
   python manage.py createsuperuser
   ```

5. **Start the server**:
   ```powershell
   python manage.py runserver 0.0.0.0:8000
   ```

   Or with Daphne for WebSocket support:
   ```powershell
   daphne -b 0.0.0.0 -p 8000 sign_language_api.asgi:application
   ```

### Frontend (Flutter)

1. **Get dependencies**:
   ```powershell
   cd frontend
   flutter pub get
   ```

2. **Run on device/emulator**:
   ```powershell
   flutter run
   ```

3. **Run on web**:
   ```powershell
   flutter run -d chrome
   ```

## API Endpoints

### Health Check
- `GET /api/health/` - Check API status

### Sign Detection
- `POST /api/detect/` - Detect sign from landmarks
  ```json
  {
    "landmarks": [[x, y, z], ...],  // 21 landmarks
    "user_id": "optional-user-id"
  }
  ```

### Gesture Data
- `POST /api/gestures/` - Upload batch of gestures
- `GET /api/gestures/stats/{user_id}/` - Get user stats
- `GET /api/gestures/thresholds/{user_id}/` - Get personalized thresholds

### Users
- `POST /api/users/get_or_create_by_device/` - Get or create user profile

### Signs Reference
- `GET /api/signs/alphabet/` - Get ASL alphabet reference

### Admin
- `GET /api/admin/analytics/` - System-wide analytics

## WebSocket Endpoints

### Real-time Detection
- `ws://localhost:8000/ws/detection/`
  ```json
  // Send:
  {"type": "detect", "landmarks": [...]}
  
  // Receive:
  {"type": "detection_result", "sign": "A", "confidence": 0.85}
  ```

### Session-based Detection
- `ws://localhost:8000/ws/session/{session_id}/`

## Features

- ✅ Real-time ASL sign detection
- ✅ REST API for detection and data collection
- ✅ WebSocket support for live streaming
- ✅ User profiles and gesture history
- ✅ Personalized detection thresholds
- ✅ Analytics and progress tracking
- ✅ Beautiful Flutter UI with dark theme
- ✅ Camera integration
- ✅ Text output with copy/clear functions

## Tech Stack

### Backend
- Python 3.10+
- Django 4.2
- Django REST Framework
- Django Channels (WebSocket)
- SQLite (development)

### Frontend
- Flutter 3.x
- Provider (state management)
- Camera plugin
- WebSocket support
- Material Design 3

## License

MIT License
