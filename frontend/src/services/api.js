const API_BASE = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

export function getApiBase() {
  return API_BASE;
}

export async function detectImage(file) {
  const form = new FormData();
  form.append("image", file);

  const response = await fetch(`${API_BASE}/api/detect`, {
    method: "POST",
    body: form,
  });

  let body = null;
  try {
    body = await response.json();
  } catch {
    body = null;
  }

  if (!response.ok) {
    const detail = body?.detail;
    const message = detail
      ? typeof detail === "string"
        ? detail
        : JSON.stringify(detail)
      : `Request failed (HTTP ${response.status}).`;
    throw new Error(message);
  }

  return body;
}

export function resultImageUrl(path) {
  return `${API_BASE}${path}`;
}