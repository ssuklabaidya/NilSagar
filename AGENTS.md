# AGENTS.md

## Mission

Small full-stack prototype for marine Side-Scan Sonar (SSS) object detection.

```
React/Vite upload → FastAPI → YOLO best.pt → detections + annotated image → frontend result
```

Prototype for demonstration, not production navigation/GIS. Never fabricate model outputs, GPS data, or capabilities.

## Product principles

- Correct, clear, boring, explicit code; small complete system over large architecture.
- Preserve the distinction between real metadata and synthetic demonstration data.
- Keep frontend/backend responsibilities clearly separated.

## Visual/UI direction

Practical scientific/engineering tool, image-first. No AI-generator look: no pill-shaped everything, no giant rounded cards, no sci-fi/neon palettes, no gradients/glows/glassmorphism, no fake scanning-line/particle animations, no decorative dashboards/charts, no animation beyond necessary states. Make idle/selected/processing/success/error states obvious. The annotated result image gets prominent space.

## Required stack

- Frontend: React + Vite (plain JS in this repo, `frontend/`), drag-and-drop upload, responsive. **No YOLO inference in the browser.**
- Backend: Python + FastAPI (`backend/`), YOLO via `best.pt`, CORS for local dev.

## Backend contract

Endpoints (FastAPI `/docs` must stay usable):

- `GET /`
- `GET /health` — status + whether model loaded
- `POST /api/detect` — `multipart/form-data`, field `image`

Detection object (stable JSON, never raw YOLO/framework objects):

```json
{
  "class_id": 1,
  "class_name": "shipwreck",
  "confidence": 0.87,
  "bbox": { "x1": 120, "y1": 80, "x2": 340, "y2": 250 }
}
```

- Class names come from the loaded model's `names` mapping; never hard-code class IDs. Expected classes: `submarine_pipeline`, `shipwreck`, `ghost_net`, `mine_cylinder` — model is authoritative.
- Annotated result image includes box + class + confidence. Return a URL to the saved file (`/outputs/{name}`, served via StaticFiles), not base64 in JSON.

## Model lifecycle

- `MODEL_PATH` points at `backend/models/best.pt`. Load once at startup via lifespan; never `YOLO(...)` per request.
- Missing/unloadable model → clear message surfaced in `/health` and a 503 from `/api/detect`; the app must still start/run for grading without the model.
- `CONFIDENCE_THRESHOLD` (default `0.25`) is the only confidence cutoff. UI percentages are "model confidence", not calibrated probability.

## Image handling

- Current Sonar-Drishti data is pre-prepared tiles: do NOT reapply Lee filter/CLAHE or other preprocessing. Keep inference preprocessing minimal; any raw SSS preprocessing later must be a separate configurable stage.
- Uploads are untrusted: validate content type (`.jpg/.jpeg/.png`), enforce `MAX_UPLOAD_MB`, never trust filenames, use random temp names, never execute uploads, delete temp uploads after processing. Save annotated results under `OUTPUT_DIRECTORY` (`backend/outputs/`).

## Geolocation (honest only)

- If usable GPS exists in image EXIF metadata, expose it with `source: "image metadata"`.
- Otherwise return `{"available": false, "latitude": null, "longitude": null, "source": null}`. UI shows: `Geotagging unavailable — no usable location metadata found.`
- Synthetic coordinates allowed only for demos, visibly labelled `Synthetic location`, never passed off as real. Never assign random coords to detections. True georeferencing needs navigation/sonar geometry; keep an extension point in `services/georeference.py`, don't fake it.

## Config

Centralized in `backend/app/config.py` from env vars (see `backend/.env.example`): `MODEL_PATH`, `CONFIDENCE_THRESHOLD`, `CORS_ORIGINS`, `OUTPUT_DIRECTORY`, `MAX_UPLOAD_MB`. Never commit secrets.

## Errors

Clear human-readable errors to frontend for: missing image, unsupported/corrupted format, missing model, inference/metadata failure, internal errors. No stack traces to users; log details server-side. Handle these in route code, not middleware magic.

## Project structure

```text
visuals/                      (this repo)
├── backend/
│   ├── app/
│   │   ├── main.py           # FastAPI app, CORS, /outputs static mount, lifespan model load
│   │   ├── config.py         # central env config
│   │   ├── api/routes.py     # / , /health, /api/detect
│   │   ├── schemas/detection.py
│   │   └── services/
│   │       ├── detector.py       # model load + inference, returns (annotated_rgb, detections)
│   │       ├── metadata.py       # EXIF inspection
│   │       └── georeference.py   # extension point only, no fake georef
│   ├── models/               # put supplied best.pt here
│   ├── outputs/              # annotated results (gitignored at runtime)
│   ├── requirements.txt
│   └── .env.example
└── frontend/
    ├── src/
    │   ├── components/ImageUploader/
    │   ├── components/DetectionResult/
    │   ├── components/LocationInfo/
    │   ├── services/api.js    # reads VITE_API_BASE_URL, default http://localhost:8000
    │   ├── App.jsx
    │   └── main.jsx
    ├── public/
    ├── index.html
    ├── package.json
    └── vite.config.js
```

## Dev commands

Backend: `http://localhost:8000`, docs `/docs`. Use the **conda env `hackathon2026`** (target machine runs it via the Anaconda/Miniconda PowerShell prompt); manage envs by absolute path — `conda run -n hackathon2026 ...` or `E:\cs\conda_venvs\hackathon2026\python.exe`.

```bash
cd backend
conda install fastapi uvicorn python-multipart pydantic python-dotenv   # once, into hackathon2026
conda run -n hackathon2026 uvicorn app.main:app --reload
```

Frontend: `http://localhost:5173`. Node is managed by a local nvm install (e.g. `C:\Users\operator\AppData\Local\Author Software\nvm\installs\v24.21.0`), not on the shell PATH, so call node/npm by full path or from the nvm shell.

```bash
cd frontend
npm install
npm run dev
```

Fallback (only if the conda env is unusable): `python -m venv .venv` in `backend/`, install `requirements.txt`, run uvicorn; `.venv` is gitignored.

## Scope guard (do not implement unless explicitly requested)

XTF/sonar-log parsing, ping-level processing, vessel-motion/heave/pitch/roll compensation, full sonar coordinate transforms, production georeferencing, multi-AUV tracking, survey databases, auth, cloud deploy, live sonar streaming, advanced segmentation, retraining, confidence calibration, GIS infrastructure, queues/microservices, Kubernetes, GPU orchestration, premature optimization.

## Working method

1. Inspect existing code before creating files; make the smallest coherent change.
2. Reuse clear correct code; avoid new dependencies without concrete reason.
3. Test the affected path (backend: re-run uvicorn + curl `/health` and `/api/detect`; frontend: `npm run build`).
4. Keep API contract simple and stable; update README/config docs when setup or behavior changes.
5. Never invent model outputs, GPS data, or unsupported capabilities.