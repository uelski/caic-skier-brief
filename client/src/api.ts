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

export async function predictText(summaryText: string) {
  const r = await fetch(`${API}/api/predict-text`, {
    method: "POST",
    headers: {"Content-Type":"application/json"},
    body: JSON.stringify({ summaryText }),
  });
  if (!r.ok) throw new Error(await r.text());
  return r.json() as Promise<{ mode: "baseline" | "trained" | "fallback"; levels: Record<string, number> }>;
}
