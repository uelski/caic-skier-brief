# /ml

- **Artifact**: `data/normalized/forecasts.json`
- **Validate**: `python ml/scripts/validate.py`
- **Baseline eval**: `python ml/scripts/baseline_eval.py`

Notes:
- `forecasts.json` may include either textual levels ("low"/"moderate"/...) or numeric `levels_1to5`. Both are supported by the scripts.
- Keep `date` as `YYYY-MM-DD`. `id` is optional but recommended.
