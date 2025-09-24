import json
import pandas as pd
from bs4 import BeautifulSoup as bsoup
import os
import re, hashlib
from typing import Dict, Any

# Get the directory of this script
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)  # Go up one level from scripts/ to ml/

IN = os.path.join(project_root, 'data', 'raw', 'all_new_forecasts.json')
MANUAL_FORECASTS = os.path.join(project_root, 'data', 'raw', 'manual_forecasts.json')
OUT = os.path.join(project_root, 'data', 'normalized', 'forecasts_normalized.json') 
FINAL_OUT = os.path.join(project_root, 'data', 'normalized', 'forecasts.json') 

# for mapping
LEVEL_1TO5 = {
    "earlyseason": 1,   # or set to None if you prefer to exclude; 1 keeps pipelines simple
    "low": 1,
    "moderate": 2,
    "considerable": 3,
    "high": 4,
    "extreme": 5,
}

LEVEL_0TO4 = {
    "earlyseason": 0,
    "low": 1,
    "moderate": 2,
    "considerable": 3,
    "high": 4,
    "extreme": 5,
}

PHRASE_RULES = [
    # unify common variants to canonical tokens used by your baseline/rules later
    (r"\bwind[-\s]?drift(?:ed|ing)?\b", "wind drifted"),
    (r"\bwind[-\s]?slab[s]?\b", "wind slab"),
    (r"\bstorm[-\s]?slab[s]?\b", "storm slab"),
    (r"\bpersistent\s+weak\s+layer\b", "persistent weak layer"),
    (r"\bpersistent[-\s]?slab[s]?\b", "persistent slab"),
    (r"\bfacet(ed)?\b", "facets"),
    (r"\bnear\s*treeline\b", "near treeline"),  # unify spacing
]

NEGATION_AND_ELEVATION_TO_KEEP = {
    # keep these even in "no-stop" variant
    "no","not","nor","never","without","lack","absent",
    "above","below","near","at","treeline","ridgeline","ridge","gully","gullies"
}

# Simple tokenizer (avoid heavyweight downloads). Works fine for baseline prep.
TOKEN_RE = re.compile(r"[A-Za-z][A-Za-z\-']+|[0-9]+") 

# helpers for transform_data
def map_level(d: str, mapping: Dict[str, int]) -> int:
    return mapping.get(d.strip().lower(), mapping.get("low", 1))

def normalize_summary(text: str) -> str:
    if not text:
        return ""
    s = text.strip().lower()
    # light canonicalization
    for pat, repl in PHRASE_RULES:
        s = re.sub(pat, repl, s, flags=re.IGNORECASE)
    # collapse whitespace
    s = re.sub(r"\s+", " ", s)
    return s

def no_stop_variant(text: str) -> str:
    """Remove *generic* filler but KEEP domain-critical tokens (negation/elevation)."""
    if not text:
        return ""
    toks = TOKEN_RE.findall(text.lower())
    out = []
    for tok in toks:
        if tok in NEGATION_AND_ELEVATION_TO_KEEP:
            out.append(tok)
            continue
        # ultra-lightweight stopword heuristic (keep numerics and short domain words)
        if tok.isdigit():
            out.append(tok); continue
        if len(tok) <= 2:  # keep short tokens minimal
            continue
        # drop very common filler; keep modal verbs (could, may, might) since they signal likelihood
        if tok in {"the","a","an","and","or","but","of","in","on","for","to","with","as","by","be","is","are","was","were","it","this","that","these","those"}:
            continue
        out.append(tok)
    return " ".join(out)

def mk_id(date: str, summary: str) -> str:
    """Stable id = YYYY-MM-DD + 8-char hash of summary."""
    h = hashlib.sha1(summary.encode("utf-8")).hexdigest()[:8]
    return f"{date}_{h}"

def transform_data(rec: Dict[str, Any]) -> Dict[str, Any]:
    date = rec.get("date") or ""
    summary_raw = rec.get("Summary_clean") or ""

    levels_text = {
        "above_treeline": (rec.get("Above Treeline") or "").strip().lower(),
        "treeline":       (rec.get("Treeline") or "").strip().lower(),
        "below_treeline": (rec.get("Below Treeline") or "").strip().lower(),
    }

    levels_1to5 = {k: map_level(v, LEVEL_1TO5) for k, v in levels_text.items()}
    levels_0to4 = {k: map_level(v, LEVEL_0TO4) for k, v in levels_text.items()}

    summary_norm = normalize_summary(summary_raw)
    summary_no_stop = no_stop_variant(summary_norm)

    out = {
        "id": mk_id(date, summary_raw) if rec.get("id") is None else rec.get("id"),
        "date": date,
        "datetime": rec.get("datetime"),
        "summary": summary_raw,          # keep original text
        "summary_norm": summary_norm,    # lowercased + canonicalized phrases
        "summary_no_stop": summary_no_stop,  # optional variant (domain-aware)
        "levels_text": levels_text,      # strings
        "levels_1to5": levels_1to5,      # integers 1..5
        "levels_0to4": levels_0to4,      # integers 0..4 (your legacy)
    }
    return out

# helpers for normalize_data
def strip_html(html):
    text = str(html)
    return bsoup(text, "html.parser").get_text()

def remove_empty_fields(df: pd.DataFrame) -> pd.DataFrame:
    df = df[df['Summary_clean'] != ""]
    df = df[(df['Below Treeline'] != "noRating") & (df['Treeline'] != "noRating") & (df['Above Treeline'] != "noRating")]
    return df

def create_manual_forecasts_df():
    with open(MANUAL_FORECASTS, 'r') as f:
        manual_forecasts = json.load(f)
    manual_forecast_df = pd.DataFrame(manual_forecasts)
    manual_forecast_df["datetime"] = pd.to_datetime(manual_forecast_df["date"])
    return manual_forecast_df

def normalize_data(data_path: str):

    with open(data_path, 'r') as f:
        forecasts = json.load(f)

    # remove polygons and clean summary
    for forecast in forecasts:
        forecast.pop('polygons', None)
        
        summary_dict = json.loads(forecast['Summary'])
        forecast['Summary_en'] = summary_dict.get('en', None)
    
    #create dataframe
    forecast_df = pd.DataFrame(forecasts)

    # strip html  
    forecast_df['Summary_clean'] = forecast_df['Summary_en'].apply(strip_html)

    # remove empty fields
    forecast_df = remove_empty_fields(forecast_df)

    # make datetime
    forecast_df["datetime"] = pd.to_datetime(forecast_df["date"])

    # choose fields
    df = forecast_df[["id", "datetime", "Above Treeline", "Treeline", "Below Treeline", "Summary_clean", "date"]]

    # merge with manual forecasts
    manual_forecast_df = create_manual_forecasts_df()
    df = pd.concat([df, manual_forecast_df], ignore_index=True)
    # write to json file
    df.to_json(OUT, orient='records')
    

def main():
    data_path = IN
    normalize_data(data_path)
    with open(OUT, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Accept either a list or a dict of records
    if isinstance(data, dict):
        data = [data]

    out = [transform_data(r) for r in data]
    # sort by date asc
    out.sort(key=lambda r: r["date"])

    with open(FINAL_OUT, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)

    print(f"Wrote {FINAL_OUT} with {len(out)} rows")
    

if __name__ == '__main__':
    main()