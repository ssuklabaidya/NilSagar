export default function LocationInfo({ geolocation }) {
  return (
    <div className="location-panel">
      <span className="location-label">Location</span>

      {!geolocation || !geolocation.available ? (
        <span className="location-unavailable">
          Geotagging unavailable — no usable location metadata found.
        </span>
      ) : (
        <dl className="location-dl">
          <div>
            <dt>Latitude</dt>
            <dd>{geolocation.latitude}</dd>
          </div>
          <div>
            <dt>Longitude</dt>
            <dd>{geolocation.longitude}</dd>
          </div>
          <div>
            <dt>Source</dt>
            <dd>
              {geolocation.source}
              {geolocation.source === "synthetic" && (
                <span className="badge-synthetic">Synthetic location</span>
              )}
            </dd>
          </div>
        </dl>
      )}
    </div>
  );
}