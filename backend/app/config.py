import os

from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _resolve(path, default):
    value = os.getenv(path, default).strip()
    if not os.path.isabs(value):
        value = os.path.join(BASE_DIR, value)
    return value


def _origin_list(value):
    return [origin.strip() for origin in value.split(",") if origin.strip()]


def _parse_confidence(val_str, default=0.25):
    try:
        val = float(val_str)
        # If entered as a percentage (e.g. 25 instead of 0.25), normalize to [0.0, 1.0]
        if val > 1.0 and val <= 100.0:
            val = val / 100.0
        return max(0.0, min(1.0, val))
    except (ValueError, TypeError):
        return default


MODEL_PATH = _resolve("MODEL_PATH", "models/best.pt")
CONFIDENCE_THRESHOLD = _parse_confidence(os.getenv("CONFIDENCE_THRESHOLD", "0.25"))
CORS_ORIGINS = _origin_list(os.getenv("CORS_ORIGINS", "http://localhost:5173"))
OUTPUT_DIRECTORY = _resolve("OUTPUT_DIRECTORY", "outputs")
MAX_UPLOAD_MB = int(os.getenv("MAX_UPLOAD_MB", "10"))

ALLOWED_CONTENT_TYPES = {"image/jpeg", "image/png"}
CONTENT_TYPE_EXTENSION = {"image/jpeg": ".jpg", "image/png": ".png"}

os.makedirs(OUTPUT_DIRECTORY, exist_ok=True)