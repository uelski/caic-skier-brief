import pandas as pd
import numpy as np
import json
from pathlib import Path
from sklearn.model_selection import train_test_split
from dataclasses import dataclass

# default path
DEFAULT_PATH = Path(__file__).parent.parent / "data" / "normalized" / "forecasts.json"

@dataclass
class Splits:
    X_train: list[str]
    X_test: list[str]
    y_train: dict[str, np.ndarray]  # keys: "btl","tl","atl" (int64, 0..4)
    y_test: dict[str, np.ndarray]

def _read_json_any(path: Path) -> list[dict]:
    txt = path.read_text(encoding="utf-8")
    try:
        data = json.loads(txt)
        return data if isinstance(data, list) else [data]
    except json.JSONDecodeError:
        rows = []
        for line in txt.splitlines():
            line = line.strip()
            if line:
                rows.append(json.loads(line))
        return rows

def _extract_texts_and_labels(rows: list[dict], text_field: str) -> tuple[list[str], dict[str, np.ndarray]]:
    texts: list[str] = []
    btl, tl, atl = [], [], []
    for r in rows:
        texts.append(r[text_field])
        lv = r["levels_0to4"]
        btl.append(int(lv["below_treeline"]))  # 1...5
        tl.append(int(lv["treeline"]))
        atl.append(int(lv["above_treeline"]))
    y = {
        "btl": np.array(btl, dtype=np.int64),
        "tl":  np.array(tl,  dtype=np.int64),
        "atl": np.array(atl, dtype=np.int64),
    }
    return texts, y

def make_splits(
    json_path: Path = DEFAULT_PATH,
    text_field: str = "summary",
    test_size: float = 0.2,
    random_state: int = 42,
    ) -> Splits:
    rows = _read_json_any(json_path)
    texts, y = _extract_texts_and_labels(rows, text_field=text_field)

    idx = np.arange(len(texts))
    tr_idx, te_idx = train_test_split(
        idx, test_size=test_size, random_state=random_state, shuffle=True
    )

    X_train = [texts[i] for i in tr_idx]
    X_test  = [texts[i] for i in te_idx]
    y_train = {k: v[tr_idx] for k, v in y.items()}
    y_test  = {k: v[te_idx] for k, v in y.items()}
    return Splits(X_train, X_test, y_train, y_test)

def stack_targets(y: dict[str, np.ndarray]) -> np.ndarray:
    """Optional helper: (N,3) matrix in order [btl, tl, atl]."""
    return np.stack([y["btl"], y["tl"], y["atl"]], axis=1)