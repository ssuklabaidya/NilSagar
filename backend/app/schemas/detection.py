from typing import List, Optional

from pydantic import BaseModel


class BBox(BaseModel):
    x1: float
    y1: float
    x2: float
    y2: float


class Detection(BaseModel):
    class_id: int
    class_name: str
    confidence: float
    bbox: Optional[BBox] = None


class Geolocation(BaseModel):
    available: bool = False
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    source: Optional[str] = None


class ImageInfo(BaseModel):
    filename: str
    width: int
    height: int


class DetectResponse(BaseModel):
    success: bool
    image: ImageInfo
    detections: List[Detection]
    geolocation: Geolocation
    annotated_image: str