import json, re, os
from typing import Dict

script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)
PATH = os.path.join(project_root, 'data', 'normalized', 'forecasts.json') 

MAP_1TO5 = {"earlyseason":1,"low":1,"moderate":2,"considerable":3,"high":4,"extreme":5}

KEYWORDS = [
    (re.compile(r"\bconsiderable\b", re.I), {"below_treeline": +1, "treeline": +1, "above_treeline": +1}),
    (re.compile(r"\bhigh\b", re.I),         {"treeline": +1, "above_treeline": +1}),
    (re.compile(r"\blower\b", re.I),        {"below_treeline": -1}),
    (re.compile(r"\bwind slab|wind[-\s]?drift(?:ed|ing)?\b", re.I), {"above_treeline": +1}),
    (re.compile(r"\bstorm slab\b", re.I),   {"above_treeline": +1}),
    (re.compile(r"\bpersistent slab|facets|persistent weak layer\b", re.I), {"treeline": +1}),
]

def clamp(x: int) -> int: return 1 if x < 1 else 5 if x > 5 else x

def rule_based_predict(text: str) -> Dict[str, int]:
    # default to 1 for baseline predictions and add if there is a keyword in summary
    s = {"below_treeline": 1, "treeline": 1, "above_treeline": 1}
    txt = (text or "").lower()
    for rx, delta in KEYWORDS:
        if rx.search(txt):
            for k, v in delta.items():
                s[k] += v
    return {k: clamp(v) for k, v in s.items()}

def gold_levels(rec: Dict) -> Dict[str, int]:
    if "levels_1to5" in rec:
        return rec["levels_1to5"]
    tt = {
        "above_treeline": str(rec["Above Treeline"]).lower(),
        "treeline": str(rec["Treeline"]).lower(),
        "below_treeline": str(rec["Below Treeline"]).lower(),
    }
    return {k: MAP_1TO5[v] for k, v in tt.items()}

def get_summary(rec: Dict) -> str:
    for k in ("summary","summary_no_stop","summary_norm"):
        if k in rec and str(rec[k]).strip():
            return str(rec[k])
    return ""

data = json.load(open(PATH, "r", encoding="utf-8"))
B=T=A=0
for r in data:
    pred = rule_based_predict(get_summary(r))
    gold = gold_levels(r)
    B += pred["below_treeline"] == gold["below_treeline"]
    T += pred["treeline"] == gold["treeline"]
    A += pred["above_treeline"] == gold["above_treeline"]

n = max(1, len(data))
print("Baseline accuracy (BTL, TL, ATL):",
      round(B/n, 3), round(T/n, 3), round(A/n, 3))
