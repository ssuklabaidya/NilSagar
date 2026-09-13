"""EXIF metadata inspection.

Only reads geographic metadata from uploaded images. Source is
"image metadata" when GPS data is present and usable; otherwise we report
the full unavailable payload and never invent coordinates.
"""

import logging

from PIL import Image
from PIL.ExifTags import GPSTAGS, TAGS

from app.schemas.detection import Geolocation

logger = logging.getLogger(__name__)

_GPS_TAG = 0x8825


def _to_float(value):
    if value is None:
        return None
    return value.numerator / value.denominator


def inspect(image_path):
    """Return a Geolocation from EXIF GPS data if present, else unavailable."""
    try:
        with Image.open(image_path) as img:
            exif = img._getexif() or {}
    except Exception as exc:
        logger.warning("Could not read EXIF from %s: %s", image_path, exc)
        return Geolocation()

    gps_ifd = exif.get(_GPS_TAG, {})
    lat = gps_ifd.get(GPSTAGS.get(2))
    lon = gps_ifd.get(GPSTAGS.get(4))

    if lat is None or lon is None:
        return Geolocation()

    latitude = _to_float(lat) if hasattr(lat, "numerator") else lat
    longitude = _to_float(lon) if hasattr(lon, "numerator") else lon
    if latitude is None or longitude is None:
        return Geolocation()

    # EXIF latitudes are always N/S positives; apply hemisphere signs.
    if str(gps_ifd.get(GPSTAGS.get(1), "S")).upper().startswith("S"):
        latitude = -latitude
    if str(gps_ifd.get(GPSTAGS.get(3), "W")).upper().startswith("W"):
        longitude = -longitude

    return Geolocation(
        available=True,
        latitude=round(float(latitude), 7),
        longitude=round(float(longitude), 7),
        source="image metadata",
    )