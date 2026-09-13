import { useEffect, useRef, useState } from "react";

const ACCEPT = "image/jpeg,image/png,.jpg,.jpeg,.png";
const VALID_TYPES = new Set(["image/jpeg", "image/png"]);

function formatBytes(bytes) {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(0)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

export default function ImageUploader({ onChange, onAnalyze, file, busy }) {
  const inputRef = useRef(null);
  const [dragOver, setDragOver] = useState(false);
  const [fileError, setFileError] = useState(null);

  const previewUrl = file ? URL.createObjectURL(file) : null;

  useEffect(() => {
    return () => {
      if (previewUrl) URL.revokeObjectURL(previewUrl);
    };
  }, [previewUrl]);

  function selectFile(nextFile) {
    setFileError(null);
    if (!nextFile) return;
    if (!VALID_TYPES.has(nextFile.type)) {
      setFileError("Unsupported file type. Use JPG or PNG.");
      return;
    }
    onChange(nextFile);
  }

  function clearFile() {
    onChange(null);
    setFileError(null);
    if (inputRef.current) inputRef.current.value = "";
  }

  return (
    <section className="uploader">
      <div
        className={`drop-zone${dragOver ? " drag-over" : ""}`}
        onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
        onDragLeave={() => setDragOver(false)}
        onDrop={(e) => {
          e.preventDefault();
          setDragOver(false);
          selectFile(e.dataTransfer.files?.[0]);
        }}
      >
        <input
          id="sonar-file-input"
          ref={inputRef}
          type="file"
          accept={ACCEPT}
          onChange={(e) => selectFile(e.target.files?.[0])}
          hidden
        />

        {previewUrl ? (
          <div className="preview-wrap">
            <img className="preview" src={previewUrl} alt="Selected sonar image" />
            <div className="preview-meta">
              <span className="preview-filename">{file.name}</span>
              <span>{formatBytes(file.size)}</span>
            </div>
          </div>
        ) : (
          <div
            className="drop-hint-area"
            onClick={() => inputRef.current?.click()}
            role="button"
            tabIndex={0}
            aria-label="Select sonar image"
            onKeyDown={(e) => e.key === "Enter" && inputRef.current?.click()}
          >
            {/* Upload icon */}
            <svg
              className="drop-icon"
              width="32"
              height="32"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="1.5"
              strokeLinecap="round"
              strokeLinejoin="round"
              aria-hidden="true"
            >
              <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
              <polyline points="17 8 12 3 7 8" />
              <line x1="12" y1="3" x2="12" y2="15" />
            </svg>
            <p className="drop-hint">
              Drag &amp; drop a sonar image here, or{" "}
              <span className="link">browse</span>.{" "}
              <span style={{ display: "block", marginTop: 4 }}>JPG / PNG only.</span>
            </p>
          </div>
        )}
      </div>

      <div className="uploader-actions">
        <div style={{ display: "flex", gap: "8px", alignItems: "center" }}>
          <button
            id="select-image-btn"
            type="button"
            className="btn-secondary"
            onClick={() => inputRef.current?.click()}
            disabled={busy}
          >
            {file ? "Choose another" : "Select image"}
          </button>
          {file && (
            <button
              id="clear-image-btn"
              type="button"
              className="btn-secondary"
              onClick={clearFile}
              disabled={busy}
            >
              Clear
            </button>
          )}
          {fileError && <span className="uploader-file-error">{fileError}</span>}
        </div>

        <button
          id="analyze-btn"
          type="button"
          className="btn-primary"
          onClick={onAnalyze}
          disabled={busy || !file}
        >
          {busy && <span className="spinner" aria-hidden="true" />}
          {busy ? "Analyzing…" : "Analyze"}
        </button>
      </div>
    </section>
  );
}