import re
from typing import Dict
from .schemas import ElevBand

# Tweak these later as you like
KEYWORDS = [
    (re.compile(r"\bconsiderable\b", re.I), {"below_treeline": +1, "treeline": +1, "above_treeline": +1}),
    (re.compile(r"\bhigh\b", re.I),         {"treeline": +1, "above_treeline": +1}),
    (re.compile(r"\blower\b", re.I),        {"below_treeline": -1}),
    (re.compile(r"\bwind slab|wind[-\s]?drift(?:ed|ing)?\b", re.I), {"above_treeline": +1}),
    (re.compile(r"\bstorm slab\b", re.I),   {"above_treeline": +1}),
    (re.compile(r"\bpersistent slab|facets|persistent weak layer\b", re.I), {"treeline": +1}),
]

def clamp(x: int) -> int:
    return 1 if x < 1 else 5 if x > 5 else x

def rule_based_predict(text: str) -> Dict[ElevBand, int]:
    s = {"below_treeline": 1, "treeline": 1, "above_treeline": 1}
    txt = (text or "").lower()
    for rx, delta in KEYWORDS:
        if rx.search(txt):
            for k, v in delta.items():
                s[k] += v
    return {k: clamp(v) for k, v in s.items()}  # type: ignore
