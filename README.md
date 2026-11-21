# CVE Triage Assistant

Ranks each day's new CVEs so the most severe are reviewed first. The score is an estimate for prioritization, not a CVSS score.

## Team

- Hamzeh Abujumaa
- Hisham Obeidat

## Docker image

`hamzehabujumaa/cve-triage:0.1.0` (public on Docker Hub, model version `cve-triage-2`)

## Install

Python 3.11 or 3.12 (the pinned libraries do not install on 3.13 or newer). Put the course files in `data/` (`cves_history.csv`, `day_sample.csv`, `check_submission.py`). This folder is not in Git.

```bash
python -m venv .venv
source .venv/Scripts/activate      # Windows Git Bash; on Mac/Linux: source .venv/bin/activate
pip install -e ".[dev]"
```

## Run the pipeline (one command)

validate → split → train → evaluate, then log to MLflow (`sqlite:///mlflow.db`) and register the model as `cve-triage`:

```bash
python -m cve_triage.pipeline --register
```

This writes `reports/metrics.json` and `reports/eval_report.md`. While choosing settings, use the validation set only:

```bash
python -m cve_triage.pipeline --eval-on val
```

See the runs in MLflow with: `mlflow ui --backend-store-uri sqlite:///mlflow.db`

## Run the tests

```bash
python -m pytest -q
```

## Build and run the batch image

```bash
python -m cve_triage.pipeline --register          # creates artifacts/model.joblib
docker build --build-arg MODEL_VERSION=cve-triage-2 -t hamzehabujumaa/cve-triage:0.1.0 .
docker run --rm -v "$(pwd)/data:/data" hamzehabujumaa/cve-triage:0.1.0 \
  --input /data/day_sample.csv --output /data/ranked.csv
python data/check_submission.py data/ranked.csv
```

On Windows PowerShell, use `${PWD}` instead of `$(pwd)`. In Git Bash, prefix the run with `MSYS_NO_PATHCONV=1`.

## Results (test set: Nov–Dec 2025, K = 40)

| | v0 | Model |
|---|---|---|
| Critical-capture@K | 0.419 | 0.751 |
| HC-capture@K | 0.309 | 0.413 |

The model uses `C = 1.0`, chosen on the validation set. The targets in `config.yaml` were set from the validation set; see `docs/model_card.md`.