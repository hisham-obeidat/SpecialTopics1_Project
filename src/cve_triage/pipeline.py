"""One command: python -m cve_triage.pipeline
validate -> split -> train -> evaluate. Each step reads and writes files in artifacts/."""
import argparse
import json
import subprocess
from pathlib import Path

import mlflow
import mlflow.sklearn
import pandas as pd

from cve_triage.config import load_config, load_features
from cve_triage.evaluate import evaluate, write_reports
from cve_triage.split import remove_duplicates, time_split
from cve_triage.train import load_model, save_model, train_model
from cve_triage.validate import validate_file


def step_validate(data_path, spec, out_dir):
    df = validate_file(data_path, spec)
    df.to_pickle(out_dir / "validated.pkl")


def step_split(spec, cfg, out_dir):
    df = pd.read_pickle(out_dir / "validated.pkl")
    train, val, test = time_split(df, spec, cfg["split"]["test_months"], cfg["split"]["validation_months"])
    test, n_dup = remove_duplicates(test, train, spec)
    train.to_pickle(out_dir / "train.pkl")
    val.to_pickle(out_dir / "val.pkl")
    test.to_pickle(out_dir / "test.pkl")
    info = {"n_train": len(train), "n_val": len(val), "n_test": len(test), "n_test_duplicates_removed": n_dup}
    for name, part in [("train", train), ("val", val), ("test", test)]:
        info[f"{name}_window"] = f"{part[spec['time']].min().date()} to {part[spec['time']].max().date()}"
    (out_dir / "split.json").write_text(json.dumps(info, indent=2))
    return info


def step_train(spec, cfg, out_dir):
    train = pd.read_pickle(out_dir / "train.pkl")
    save_model(train_model(train, spec, cfg), out_dir / "model.joblib")


def step_evaluate(spec, cfg, out_dir, reports_dir, on, n_dup):
    model = load_model(out_dir / "model.joblib")
    df = pd.read_pickle(out_dir / f"{on}.pkl")
    metrics = evaluate(model, df, spec, cfg["capacity"]["k_per_day"], n_dup if on == "test" else 0)
    title = "Evaluation on the test set" if on == "test" else "Evaluation on the validation set"
    write_reports(metrics, reports_dir, title)
    return metrics


def git_commit():
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    except Exception:
        return "unknown"


def flat(prefix, d, out):
    for k, v in d.items():
        key = f"{prefix}.{k}" if prefix else str(k)
        if isinstance(v, dict):
            flat(key, v, out)
        elif isinstance(v, (int, float)):
            out[key] = float(v)
    return out


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default="config.yaml")
    ap.add_argument("--features", default="features.yaml")
    ap.add_argument("--data", default=None, help="overrides data.history in config.yaml")
    ap.add_argument("--eval-on", choices=["val", "test"], default="test",
                    help="use 'val' while choosing settings; 'test' only for the final numbers")
    ap.add_argument("--register", action="store_true", help="register the model in MLflow")
    ap.add_argument("--no-mlflow", action="store_true")
    args = ap.parse_args(argv)

    spec, cfg = load_features(args.features), load_config(args.config)
    out_dir = Path(cfg["paths"]["artifacts"])
    out_dir.mkdir(parents=True, exist_ok=True)
    reports_dir = Path(cfg["paths"]["reports"]) if args.eval_on == "test" else out_dir / "val_reports"

    step_validate(args.data or cfg["data"]["history"], spec, out_dir)
    info = step_split(spec, cfg, out_dir)
    step_train(spec, cfg, out_dir)
    metrics = step_evaluate(spec, cfg, out_dir, reports_dir, args.eval_on, info["n_test_duplicates_removed"])
    print(json.dumps({"model": metrics["model"]["critical_capture_at_k"]["overall"],
                      "v0": metrics["v0"]["critical_capture_at_k"]["overall"]}))

    if args.no_mlflow:
        return metrics
    mlflow.set_tracking_uri(cfg["mlflow"]["tracking_uri"])
    mlflow.set_experiment(cfg["mlflow"]["experiment"])
    with mlflow.start_run():
        mlflow.set_tag("git_commit", git_commit())
        mlflow.set_tag("eval_on", args.eval_on)
        params = {"model_type": cfg["model"]["type"], "k_per_day": cfg["capacity"]["k_per_day"]}
        params.update({f"clf.{k}": v for k, v in cfg["model"]["params"].items()})
        params.update({f"tfidf.{k}": v for k, v in (cfg["model"].get("tfidf") or {}).items()})
        params.update(info)
        mlflow.log_params(params)
        mlflow.log_metrics(flat("", {"model": metrics["model"], "v0": metrics["v0"],
                                     "critical_recall": metrics["critical_recall"]}, {}))
        mlflow.log_artifact(args.features)
        mlflow.log_artifact(args.config)
        mlflow.log_artifacts(str(reports_dir), artifact_path="reports")
        mlflow.sklearn.log_model(
            load_model(out_dir / "model.joblib"), artifact_path="model",
            serialization_format=mlflow.sklearn.SERIALIZATION_FORMAT_CLOUDPICKLE,
            registered_model_name=cfg["model"]["name"] if args.register else None)
    return metrics


if __name__ == "__main__":
    main()