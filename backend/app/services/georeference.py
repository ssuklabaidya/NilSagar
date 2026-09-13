"""Georeference extension point (explicitly NOT implemented).

True SSS georeferencing requires navigation/sonar geometry: vessel or AUV
position, heading, altitude/depth, range and slant-range of a ping, and the
image-to-ping mapping. None of that exists for this prototype's pre-processed
tiles.

Rules:
- Never fabricate coordinates and call them georeferenced.
- Never assign random coordinates to detections.
- Synthetic demo coordinates are allowed only in the frontend, visibly
  labelled "Synthetic location".
"""

from app.schemas.detection import Geolocation


def finalize(geolocation: Geolocation) -> Geolocation:
    """Placeholder: returns the metadata-derived geolocation unchanged.

    Hook for a future, honest georeferencing implementation.
    """
    return geolocation