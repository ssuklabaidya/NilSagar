import { useState } from "react";

import DetectionResult from "./components/DetectionResult/index.jsx";
import ImageUploader from "./components/ImageUploader/index.jsx";
import LocationInfo from "./components/LocationInfo/index.jsx";
import { detectImage } from "./services/api.js";

export default function App() {
  const [file, setFile] = useState(null);
  const [busy, setBusy] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [warning, setWarning] = useState(null);

  async function handleAnalyze() {
    if (!file || busy) return;
    setBusy(true);
    setError(null);
    setWarning(null);
    setResult(null);
    try {
      const body = await detectImage(file);
      setResult(body);
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="app">
      <header className="app-header">
        <h1>Sonar-Drishti</h1>
        <p className="tagline">Side-Scan Sonar Object Detection</p>
      </header>

      <ImageUploader
        file={file}
        busy={busy}
        onChange={setFile}
        onAnalyze={handleAnalyze}
      />

      {busy && (
        <div className="status-bar busy" role="status" aria-live="polite">
          <span className="spinner" aria-hidden="true" />
          Running inference…
        </div>
      )}

      {error && (
        <div className="status-bar error" role="alert">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none"
            stroke="currentColor" strokeWidth="2" strokeLinecap="round"
            strokeLinejoin="round" aria-hidden="true" style={{ flexShrink: 0 }}>
            <circle cx="12" cy="12" r="10" />
            <line x1="12" y1="8" x2="12" y2="12" />
            <line x1="12" y1="16" x2="12.01" y2="16" />
          </svg>
          {error}
        </div>
      )}

      {result && (
        <>
          <DetectionResult result={result} warning={warning} />
          <LocationInfo geolocation={result.geolocation} />
        </>
      )}

      <footer className="app-footer">
        Side-Scan Sonar object detection prototype · Smart India Hackathon 2026
      </footer>
    </div>
  );
}