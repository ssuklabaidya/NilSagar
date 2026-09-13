import logging
import uuid
from pathlib import Path

import numpy as np
from PIL import Image

from app import config
from app.schemas.detection import BBox, Detection

logger = logging.getLogger(__name__)

_model = None
_model_error = None


def load_model():
    """Load the YOLO checkpoint once at startup. Never call YOLO(...) per request."""
    global _model, _model_error

    _model = None
    _model_error = None

    path = Path(config.MODEL_PATH)
    if not path.exists():
        _model_error = f"Model file not found at {config.MODEL_PATH}."
        logger.error(_model_error)
        return

    try:
        from ultralytics import YOLO

        _model = YOLO(str(path))
        _model_error = None
        logger.info("Loaded model from %s (classes=%s)", config.MODEL_PATH, _model.names)
    except Exception as exc:  # pragma: no cover - depends on local env
        _model_error = f"Failed to load model from {config.MODEL_PATH}: {exc}"
        _model = None
        logger.exception("Model load failed")


def get_model_status():
    return _model, _model_error


def detect(image_path):
    """Run inference on an image file.

    Returns (annotated_rgb: np.ndarray, detections: List[Detection]).
    Raises RuntimeError when the model is unavailable or inference fails.
    """
    if _model is None:
        raise RuntimeError(_model_error or "Model is not loaded.")

    try:
        results = _model.predict(source=str(image_path), conf=config.CONFIDENCE_THRESHOLD)
    except Exception as exc:
        logger.exception("Inference failed on %s", image_path)
        raise RuntimeError(f"Inference failed: {exc}") from exc

    result = results[0]
    detections = []

    # 1. Standard bounding box detections (detection models)
    if result.boxes is not None and len(result.boxes) > 0:
        logger.info("Raw detections from model: %d box(es)", len(result.boxes))
        for i in range(len(result.boxes)):
            cls_id = int(result.boxes.cls[i])
            x1, y1, x2, y2 = (float(v) for v in result.boxes.xyxy[i].tolist())
            detections.append(
                Detection(
                    class_id=cls_id,
                    class_name=result.names[cls_id],
                    confidence=float(result.boxes.conf[i]),
                    bbox=BBox(x1=x1, y1=y1, x2=x2, y2=y2),
                )
            )

    # 2. Oriented bounding box detections (OBB models)
    elif getattr(result, "obb", None) is not None and len(result.obb) > 0:
        logger.info("Raw OBB detections from model: %d box(es)", len(result.obb))
        for i in range(len(result.obb)):
            cls_id = int(result.obb.cls[i])
            x1, y1, x2, y2 = (float(v) for v in result.obb.xyxy[i].tolist())
            detections.append(
                Detection(
                    class_id=cls_id,
                    class_name=result.names[cls_id],
                    confidence=float(result.obb.conf[i]),
                    bbox=BBox(x1=x1, y1=y1, x2=x2, y2=y2),
                )
            )

    # 3. Image classification probabilities (classification models)
    elif getattr(result, "probs", None) is not None:
        probs = result.probs
        logger.info("Classification model output (top1=%s conf=%.4f)", probs.top1, float(probs.top1conf))
        data = probs.data.cpu().numpy()
        for cls_id, conf in enumerate(data):
            conf_val = float(conf)
            if conf_val >= config.CONFIDENCE_THRESHOLD:
                detections.append(
                    Detection(
                        class_id=int(cls_id),
                        class_name=result.names[int(cls_id)],
                        confidence=round(conf_val, 4),
                        bbox=None,
                    )
                )
        detections.sort(key=lambda d: d.confidence, reverse=True)
    else:
        logger.info("No boxes, OBB, or probs returned by model")

    annotated_bgr = result.plot()
    annotated_rgb = annotated_bgr[:, :, ::-1]  # BGR -> RGB
    return annotated_rgb, detections


def save_annotated(annotated_rgb):
    """Persist the annotated image under OUTPUT_DIRECTORY, return its URL path."""
    name = f"result_{uuid.uuid4().hex}.png"
    output_path = Path(config.OUTPUT_DIRECTORY) / name
    Image.fromarray(np.asarray(annotated_rgb, dtype=np.uint8)).save(output_path, format="PNG")
    return f"/outputs/{name}"