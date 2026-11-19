"""Batch ranking: rank one day's CVEs with the packaged model.

python -m cve_triage.batch --input day.csv --output ranked.csv
"""
import argparse
import os
from pathlib import Path

import pandas as pd

from cve_triage.config import load_features
from cve_triage.ranking import rank_day
from cve_triage.train import load_model, predict_proba

DEFAULT_MODEL = os.environ.get("CVE_TRIAGE_MODEL", "artifacts/model.joblib")
DEFAULT_FEATURES = os.environ.get("CVE_TRIAGE_FEATURES", "features.yaml")
DEFAULT_VERSION = os.environ.get("CVE_TRIAGE_MODEL_VERSION", "cve-triage-dev")


def rank_file(input_path, output_path, model_path, features_path, model_version):
    spec = load_features(features_path)
    day = pd.read_csv(input_path, dtype=str, keep_default_na=False, na_values=[""])
    needed = [spec["id"], spec["time"], "cwe_ids"]
    missing = [c for c in needed if c not in day.columns]
    if missing:
        raise SystemExit(f"Input is missing required columns: {missing}")

    model = load_model(model_path)
    p_crit, p_high = predict_proba(model, day)
    ranked = rank_day(day, p_crit, p_high, spec)
    ranked["model_version"] = model_version
    ranked = ranked[[spec["id"], "rank", "score", "model_version"]]
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    ranked.to_csv(output_path, index=False)
    return ranked


def main(argv=None):
    ap = argparse.ArgumentParser(description="Rank one day of CVEs.")
    ap.add_argument("--input", required=True)
    ap.add_argument("--output", required=True)
    ap.add_argument("--model", default=DEFAULT_MODEL)
    ap.add_argument("--features", default=DEFAULT_FEATURES)
    ap.add_argument("--model-version", default=DEFAULT_VERSION)
    args = ap.parse_args(argv)
    ranked = rank_file(args.input, args.output, args.model, args.features, args.model_version)
    print(f"Ranked {len(ranked)} CVEs -> {args.output}")


if __name__ == "__main__":
    main()