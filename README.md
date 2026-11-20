# \# CVE Triage Assistant

# 

# Ranks each day's new CVEs so the most severe are reviewed first. The score is an estimate for prioritization, not a CVSS score.

# 

# \## Team

# \- Hamzeh abujumaa

# \- Hisham obiedat

# 

# \## Docker image

# `hamzehabujumaa/cve-triage:0.1.0` (public on Docker Hub, model version `cve-triage-2`)

# 

# \## Install

# Python 3.11. Put the course files in `data/` (`cves\_history.csv`, `day\_sample.csv`, `check\_submission.py`). This folder is not in Git.

# ```bash

# python -m venv .venv

# source .venv/Scripts/activate      # Windows Git Bash; on Mac/Linux: source .venv/bin/activate

# pip install -e ".\[dev]"

# ```

# 

# \## Run the pipeline (one command)

# validate → split → train → evaluate, then log to MLflow (`sqlite:///mlflow.db`) and register the model as `cve-triage`:

# ```bash

# python -m cve\_triage.pipeline --register

# ```

# This writes `reports/metrics.json` and `reports/eval\_report.md`. While choosing settings, use the validation set only:

# ```bash

# python -m cve\_triage.pipeline --eval-on val

# ```

# See the runs in MLflow with: `mlflow ui --backend-store-uri sqlite:///mlflow.db`

# 

# \## Run the tests

# ```bash

# python -m pytest -q

# ```

# 

# \## Build and run the batch image

# ```bash

# python -m cve\_triage.pipeline --register          # creates artifacts/model.joblib

# docker build --build-arg MODEL\_VERSION=cve-triage-2 -t hamzehabujumaa/cve-triage:0.1.0 .

# docker run --rm -v "$(pwd)/data:/data" hamzehabujumaa/cve-triage:0.1.0 \\

# &#x20; --input /data/day\_sample.csv --output /data/ranked.csv

# python data/check\_submission.py data/ranked.csv

# ```

# On Windows PowerShell, use `${PWD}` instead of `$(pwd)`. In Git Bash, prefix the run with `MSYS\_NO\_PATHCONV=1`.

# 

# \## Results (test set: Nov–Dec 2025, K = 40)

# | | v0 | Model |

# |---|---|---|

# | Critical-capture@K | 0.419 | 0.767 |

# | HC-capture@K | 0.309 | 0.416 |

# 

# The targets in `config.yaml` were set from the validation set; see `docs/model\_card.md`.

