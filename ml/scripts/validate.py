import json, sys, re
from typing import Dict
import os

script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)
PATH = os.path.join(project_root, 'data', 'normalized', 'forecasts.json') 

ALLOWED_TEXT = {"earlyseason","low","moderate","considerable","high","extreme"}
MAP_1TO5 = {"earlyseason":1,"low":1,"moderate":2,"considerable":3,"high":4,"extreme":5}
DATE_RX = re.compile(r"^\d{4}-\d{2}-\d{2}$")

def coerce_gold(rec: Dict) -> Dict[str, int]:
    # Prefer numeric if present
    if "levels_1to5" in rec:
        lv = rec["levels_1to5"]
        assert set(lv.keys()) == {"above_treeline","treeline","below_treeline"}
        for v in lv.values():
            assert isinstance(v, int) and 1 <= v <= 5
        return lv
    # Else map textual
    if {"Above Treeline","Treeline","Below Treeline"} <= set(rec.keys()):
        tt = {
            "above_treeline": str(rec["Above Treeline"]).strip().lower(),
            "treeline": str(rec["Treeline"]).strip().lower(),
            "below_treeline": str(rec["Below Treeline"]).strip().lower(),
        }
        assert set(tt.values()) <= ALLOWED_TEXT
        return {k: MAP_1TO5[v] for k, v in tt.items()}
    raise AssertionError("No recognizable levels in record")

def get_summary(rec: Dict) -> str:
    for key in ("summary","summary_no_stop","summary_norm"):
        if key in rec and str(rec[key]).strip():
            return str(rec[key])
    raise AssertionError("Missing summary/summary_no_stop/summary_norm")

def main():
    data = json.load(open(PATH, "r", encoding="utf-8"))
    assert isinstance(data, list) and len(data) > 0

    seen_ids = set()
    for i, rec in enumerate(data):
        # date
        assert "date" in rec and DATE_RX.match(str(rec["date"])), f"Bad date at idx {i}"
        # id (optional but nice); if present ensure uniqueness
        if "id" in rec:
            assert rec["id"] not in seen_ids, f"Duplicate id at idx {i}"
            seen_ids.add(rec["id"])
        # summary present
        _ = get_summary(rec)
        # levels present/coercible
        _ = coerce_gold(rec)

    print(f"OK: {len(data)} records validated in {PATH}")

if __name__ == "__main__":
    try:
        main()
    except AssertionError as e:
        print("VALIDATION ERROR:", e)
        sys.exit(1)
