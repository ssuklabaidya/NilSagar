# Place the supplied YOLO checkpoint here as `best.pt`.
#
# The repo intentionally does not ship the model. The app starts fine without
# it: `/health` reports the model as not loaded and `POST /api/detect` returns
# a 503 with a clear message until `best.pt` exists (path via MODEL_PATH env).