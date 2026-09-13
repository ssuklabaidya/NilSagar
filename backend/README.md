# SSS Object Detection API — Backend

FastAPI service that runs YOLO inference on uploaded sonar images and returns
detections plus an annotated result image.

## Setup

Use the conda env `hackathon2026` from an Anaconda/Miniconda PowerShell prompt
(installs fastapi/uvicorn deps once):

```powershell
conda run -n hackathon2026 pip install fastapi "uvicorn[standard]" python-multipart pydantic python-dotenv
```

Or, if the conda env is unavailable, create a plain venv:

```powershell
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
```

Place the supplied model at `models/best.pt`.

## Run

```powershell
conda run -n hackathon2026 uvicorn app.main:app --reload
```

- API: `http://localhost:8000`
- Docs: `http://localhost:8000/docs`
- Health: `http://localhost:8000/health` (reports whether the model loaded)

Without `models/best.pt` the app still starts; `/health` reports the missing
model and `POST /api/detect` returns a 503 with a clear message.

## Endpoints

- `GET /` — service info
- `GET /health` — status + model-loaded flag
- `POST /api/detect` — `multipart/form-data` field `image` (jpg/jpeg/png)

## Notes

- The model loads **once** at startup (lifespan), not per request.
- Class names come from the loaded model's `names` mapping.
- Annotated results are saved under `outputs/` and served at `/outputs/{name}`.
- Uploads are deleted from temporary storage after processing; validation,
  size limits, and output directory are controlled in `app/config.py`.