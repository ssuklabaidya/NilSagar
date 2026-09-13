import { resultImageUrl } from "../../services/api.js";

const CLASS_CHIP_MAP = {
  submarine_pipeline:        "chip-submarine_pipeline",
  pipeline_or_cable:         "chip-submarine_pipeline",
  shipwreck:                 "chip-shipwreck",
  ship:                      "chip-shipwreck",
  ghost_net:                 "chip-ghost_net",
  mine_cylinder:             "chip-mine_cylinder",
  seabed_surface:            "chip-seabed_surface",
  engineering_platform:      "chip-engineering_platform",
  airplane:                  "chip-airplane",
  underwater_residual_mound: "chip-underwater_residual_mound",
};

function formatConfidence(value) {
  return `${Math.round(value * 100)}%`;
}

function formatBbox(bbox) {
  if (!bbox) return "Image classification";
  const { x1, y1, x2, y2 } = bbox;
  return `${Math.round(x1)},${Math.round(y1)} → ${Math.round(x2)},${Math.round(y2)}`;
}

function ClassChip({ name }) {
  const cls = CLASS_CHIP_MAP[name] ?? "chip-default";
  return <span className={`class-chip ${cls}`}>{name.replace(/_/g, " ")}</span>;
}

function ConfidenceBar({ value }) {
  const pct = Math.round(value * 100);
  return (
    <div className="conf-row">
      <span className="conf-label">{pct}%</span>
      <div className="conf-bar-track" title={`Model confidence: ${pct}%`}>
        <div className="conf-bar-fill" style={{ width: `${pct}%` }} />
      </div>
      <span style={{ fontSize: "0.72rem", color: "var(--muted)", flexShrink: 0 }}>
        model conf.
      </span>
    </div>
  );
}

export default function DetectionResult({ result, warning }) {
  const { detections, image, annotated_image } = result;
  const count = detections.length;

  return (
    <div className="result-section">
      {warning && (
        <div className="status-bar" style={{
          background: "var(--warn-bg)",
          border: "1px solid var(--warn-border)",
          color: "var(--warn-text)",
          marginBottom: 12,
        }}>
          {warning}
        </div>
      )}

      <div className="result-layout">
        {/* ── Annotated image ── */}
        <div className="result-image-panel">
          <figure>
            <img
              src={resultImageUrl(annotated_image)}
              alt="Annotated sonar image with detections"
            />
            <figcaption>
              {image.filename} · {image.width}×{image.height}px
            </figcaption>
          </figure>
        </div>

        {/* ── Detections list ── */}
        <div className="detections-panel">
          <div className="detections-panel-header">
            <h2>Detections</h2>
            <span className="detection-count">{count} found</span>
          </div>

          {count > 0 ? (
            <ul className="detections">
              {detections.map((d, i) => (
                <li key={i} className="detection">
                  <div className="detection-top">
                    <ClassChip name={d.class_name} />
                    <span className="detection-bbox">{formatBbox(d.bbox)}</span>
                  </div>
                  <ConfidenceBar value={d.confidence} />
                </li>
              ))}
            </ul>
          ) : (
            <p className="no-detections">
              No detections above the confidence threshold.
            </p>
          )}
        </div>
      </div>
    </div>
  );
}