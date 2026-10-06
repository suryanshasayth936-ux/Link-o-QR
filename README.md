# Link'o'QR — Production In-Memory URL to QR Code Utility

A high-performance, lightweight, and production-ready web service that converts user-provided URLs into downloadable, customizable QR codes. Built with **FastAPI** following Clean Architecture principles with strict separation of presentation, business logic, schemas, and core configuration.

## Features

- **Direct Route Encoding**: Generated QR codes point directly to the user-provided destination URL.
- **Strict URL Validation**: Rejects malformed strings, dangerous schemes (`javascript:`, `file:`, `data:`, `ftp:`), and enforces valid domain/host requirements.
- **Pure In-Memory Processing**: Operates entirely in RAM using `io.BytesIO`. Zero temporary files or disk clutter.
- **Customizable QR Codes**:
  - Formats: High-resolution PNG and Scalable Vector Graphic (SVG).
  - Configurable error correction levels (L ~7%, M ~15%, Q ~25%, H ~30%).
  - Adjustable module box size and quiet zone border.
  - Custom foreground and background hex colors with pre-configured aesthetic palettes.
- **Multiple Consumption Interfaces**:
  - Modern web UI with live preview, copy-to-clipboard, and direct downloads.
  - JSON API endpoint (`POST /api/v1/qr/generate`) returning Base64 Data URIs.
  - Raw streaming endpoint (`GET /api/v1/qr/raw`) with HTTP cache headers.
  - Download attachment endpoint (`GET /api/v1/qr/download`).
- **Production-Ready & Fully Tested**: 100% test coverage for API routes, validation rules, and service layer.

---

## Directory Tree

```
Link'o'QR/
├── requirements.txt
├── README.md
├── src/
│   ├── __init__.py
│   ├── main.py                     # Application entrypoint & middleware
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py               # Pydantic Settings & environment config
│   │   └── exceptions.py           # Domain exceptions & error handlers
│   ├── schemas/
│   │   ├── __init__.py
│   │   └── qr.py                   # Pydantic models & strict URL validators
│   ├── services/
│   │   ├── __init__.py
│   │   └── qr_service.py           # In-memory QR rendering business logic
│   ├── api/
│   │   ├── __init__.py
│   │   ├── deps.py                 # Dependency injection providers
│   │   └── v1/
│   │       ├── __init__.py
│   │       ├── router.py           # API v1 aggregator
│   │       └── endpoints/
│   │           ├── __init__.py
│   │           └── qr.py           # QR generation & download endpoints
│   ├── static/
│   │   ├── css/
│   │   │   └── style.css           # Glassmorphic dark-theme styles
│   │   └── js/
│   │       └── app.js              # Frontend interactive controller
│   └── templates/
│       └── index.html              # Accessible HTML5 template
└── tests/
    ├── __init__.py
    ├── conftest.py                 # Shared pytest fixtures
    ├── test_qr_service.py          # Unit tests for QR business logic
    └── test_api.py                 # Integration tests for API endpoints
```

---

## Quickstart

### 1. Create and Activate Virtual Environment
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Run the Development Server
```bash
uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
```

Open your browser at:
- Web Application: [http://localhost:8000/](http://localhost:8000/)
- Interactive Swagger UI: [http://localhost:8000/docs](http://localhost:8000/docs)
- ReDoc API Documentation: [http://localhost:8000/redoc](http://localhost:8000/redoc)

### 4. Run the Test Suite
```bash
PYTHONPATH=. pytest -v
```

---

## API Reference

### `POST /api/v1/qr/generate`
Generates a QR code and returns metadata with a Base64 Data URI for direct display.

**Request Body:**
```json
{
  "url": "https://fastapi.tiangolo.com",
  "box_size": 10,
  "border": 4,
  "error_correction": "M",
  "fill_color": "#000000",
  "back_color": "#ffffff",
  "format": "png"
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "url": "https://fastapi.tiangolo.com",
  "format": "png",
  "data_uri": "data:image/png;base64,iVBORw0KGgo...",
  "box_size": 10,
  "border": 4,
  "error_correction": "M",
  "fill_color": "#000000",
  "back_color": "#ffffff"
}
```

### `GET /api/v1/qr/raw`
Streams raw image bytes directly from memory with `Cache-Control` headers.

**Query Parameters:**
- `url` (required): Target destination URL
- `box_size` (optional, default 10)
- `border` (optional, default 4)
- `error_correction` (optional, default M)
- `fill_color` (optional, default #000000)
- `back_color` (optional, default #ffffff)
- `format` (optional, `png` or `svg`)

### `GET /api/v1/qr/download`
Serves the rendered QR code as a downloadable file attachment (`Content-Disposition: attachment; filename="<filename>.<ext>"`).
