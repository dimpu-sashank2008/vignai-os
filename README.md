# VIGNAI OS — Vignan's AI Campus Operating System

> **VIGNAI OS** is an AI-Native Campus Operating System designed for Vignan University to synthesize campus grievance intelligence, departmental academic analytics, and deterministic administrative operations.

## Official Product Details

- **Name:** VIGNAI OS
- **Subtitle:** Vignan's AI Campus Operating System
- **Tagline:** *Understand. Connect. Predict. Act.*

## Architecture

```
vignai-os/
├── backend/          # FastAPI + SQLAlchemy + SQLite
│   ├── app/
│   │   ├── models/   # SQLAlchemy models
│   │   ├── schemas/  # Pydantic schemas
│   │   ├── routers/  # API endpoints
│   │   ├── services/ # Business logic + AI stub
│   │   └── ...
│   └── requirements.txt
└── frontend/         # React + Vite + TypeScript + Tailwind
    └── src/
        ├── pages/        # Route pages
        ├── components/   # Reusable UI + layout
        ├── auth/         # Auth context + guards
        └── api/          # HTTP client
```

## Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- npm 9+

### Backend

```bash
cd backend

# Create virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS/Linux

# Install dependencies
pip install -r requirements.txt

# Seed development database
python -m app.seed

# Start the server
uvicorn app.main:app --reload --port 8000
```

The API will be available at `http://localhost:8000`. Interactive docs at `http://localhost:8000/docs`.

### Frontend

```bash
cd frontend

npm install
npm run dev
```

The frontend will run at `http://localhost:5173`.
