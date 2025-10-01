const API = import.meta.env.VITE_API_BASE || "http://localhost:8000";

export async function health() {
  const r = await fetch(`${API}/api/health`);
  if (!r.ok) throw new Error("health_failed");
  return r.json();
}

export async function getLatest() {
  const r = await fetch(`${API}/api/latest`);
  if (!r.ok) throw new Error("no_latest");
  return r.json();
}

export async function getSamples(limit: number) {
  const r = await fetch(`${API}/api/samples?limit=${limit}`);
  if (!r.ok) throw new Error("no_samples");
  const data = await r.json();
  return data.forecasts; // Extract the forecasts array from the response
}

export async function getModels() {
  const r = await fetch(`${API}/api/models`);
  if (!r.ok) throw new Error("no_models");
  return r.json();
}

export async function predictText(summaryText: string, model: string) {
  const r = await fetch(`${API}/api/predict-levels`, {
    method: "POST",
    headers: {"Content-Type":"application/json"},
    body: JSON.stringify({ summaryText, model }),
  });
  if (!r.ok) throw new Error(await r.text());
  return r.json() as Promise<{ mode: "baseline" | "trained" | "fallback"; levels: Record<string, number> }>;
}
