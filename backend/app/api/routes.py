import logging
import uuid
from pathlib import Path

from fastapi import APIRouter, File, HTTPException, UploadFile
from PIL import Image

from app import config
from app.schemas.detection import DetectResponse, ImageInfo
from app.services import detector, georeference, metadata

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/")
def root():
    return {"name": "SSS Object Detection API", "docs": "/docs", "health": "/health"}


@router.get("/health")
def health():
    model, model_error = detector.get_model_status()
    return {"status": "ok", "model_loaded": model is not None, "model_error": model_error}


@router.post("/api/detect", response_model=DetectResponse)
async def detect(image: UploadFile = File(...)):
    content_type = image.content_type or ""
    if content_type not in config.ALLOWED_CONTENT_TYPES:
        raise HTTPException(415, f"Unsupported file type '{content_type}'. Use jpg/jpeg/png.")

    data = await image.read()
    if len(data) > config.MAX_UPLOAD_MB * 1024 * 1024:
        raise HTTPException(413, f"File exceeds the {config.MAX_UPLOAD_MB} MB upload limit.")

    suffix = config.CONTENT_TYPE_EXTENSION[content_type]
    tmp_path = Path(config.OUTPUT_DIRECTORY) / f"upload_{uuid.uuid4().hex}{suffix}"
    tmp_path.write_bytes(data)

    try:
        try:
            with Image.open(tmp_path) as img:
                img.load()
                width, height = img.size
        except Exception:
            logger.warning("Invalid/corrupted image upload")
            raise HTTPException(400, "Invalid or corrupted image file.")

        try:
            annotated_rgb, detections = detector.detect(tmp_path)
        except RuntimeError as exc:
            raise HTTPException(503, str(exc)) from exc

        annotated_path = detector.save_annotated(annotated_rgb)
        geolocation = georeference.finalize(metadata.inspect(tmp_path))

        return DetectResponse(
            success=True,
            image=ImageInfo(filename=image.filename or "image", width=width, height=height),
            detections=detections,
            geolocation=geolocation,
            annotated_image=annotated_path,
        )
    finally:
        try:
            tmp_path.unlink(missing_ok=True)
        except OSError:  # pragma: no cover - best-effort temp cleanup
            logger.warning("Could not remove temp upload %s", tmp_path)