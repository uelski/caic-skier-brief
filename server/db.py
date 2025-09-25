import json, os, hashlib, re
from functools import lru_cache
from typing import List, Dict, Any, Optional
from .schemas import Forecast

# Prefer ENV path; fallback to ml/data/normalized/forecasts.json
DATA_PATH = os.getenv("FORECASTS_PATH") or os.path.join(
    os.path.dirname(os.path.dirname(__file__)),  # Go up from server/ to project root
    "ml", "data", "normalized", "forecasts.json"
)

MAP_1TO5 = {"earlyseason":1,"low":1,"moderate":2,"considerable":3,"high":4,"extreme":5}

def _coerce_levels(rec: Dict[str, Any]) -> Dict[str, int]:
    if "levels_1to5" in rec:
        lv = rec["levels_1to5"]
        return {
            "below_treeline": int(lv["below_treeline"]),
            "treeline":       int(lv["treeline"]),
            "above_treeline": int(lv["above_treeline"]),
        }
    # textual keys (your earlier shape)
    tt = {
        "below_treeline": str(rec.get("Below Treeline","")).lower(),
        "treeline":       str(rec.get("Treeline","")).lower(),
        "above_treeline": str(rec.get("Above Treeline","")).lower(),
    }
    return {k: MAP_1TO5.get(v, 2) for k, v in tt.items()}  # default to 2 if odd label

def _coerce_summary(rec: Dict[str, Any]) -> str:
    for k in ("summary","summary_no_stop","summary_norm"):
        v = rec.get(k)
        if isinstance(v, str) and v.strip():
            return v
    return ""  # shouldn't happen if ML artifact is good

def _mk_id(date: str, summary: str) -> str:
    h = hashlib.sha1(summary.encode("utf-8")).hexdigest()[:8]
    return f"{date}_{h}"

@lru_cache(maxsize=1)
def load_forecasts() -> List[Forecast]:
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        raw = json.load(f)
    if not isinstance(raw, list):
        raw = [raw]

    out: List[Forecast] = []
    for r in raw:
        date = str(r.get("date",""))
        summary = _coerce_summary(r)
        levels = _coerce_levels(r)
        fid = r.get("id") or _mk_id(date, summary)
        out.append(Forecast(
            id=fid,
            date=date,
            datetime=r.get("datetime"),
            summary=summary,
            levels=levels
        ))
    # sort by date asc (YYYY-MM-DD assumed)
    out.sort(key=lambda x: x.date)
    return out

def latest() -> Optional[Forecast]:
    f = load_forecasts()
    return f[-1] if f else None

def samples(limit: int = 10) -> List[Forecast]:
    f = load_forecasts()
    return f[-limit:] if limit > 0 else []
