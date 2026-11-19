import json

import yaml

from tests.conftest import ROOT, SAMPLE
from cve_triage import pipeline


def test_pipeline_end_to_end_on_sample(tmp_path, small_cfg):
    cfg = yaml.safe_load(yaml.safe_dump(small_cfg))
    cfg["paths"] = {"artifacts": str(tmp_path / "artifacts"), "reports": str(tmp_path / "reports")}
    cfg_path = tmp_path / "config.yaml"
    cfg_path.write_text(yaml.safe_dump(cfg))
    pipeline.main(["--config", str(cfg_path), "--features", str(ROOT / "features.yaml"),
                   "--data", str(SAMPLE), "--no-mlflow"])
    metrics = json.loads((tmp_path / "reports" / "metrics.json").read_text())
    assert "critical_capture_at_k" in metrics["model"]
    assert (tmp_path / "reports" / "eval_report.md").exists()


def test_model_meets_targets(cfg):
    """Checks the committed final run (reports/metrics.json) against the config.yaml targets."""
    m = json.loads((ROOT / "reports" / "metrics.json").read_text())
    t = cfg["targets"]
    crit = m["model"]["critical_capture_at_k"]
    assert crit["overall"] >= t["critical_capture_at_k"]["overall"]
    groups = [v for k, d in crit.items() if k.startswith("by_") for v in d.values() if v is not None]
    assert min(groups) >= t["critical_capture_at_k"]["min_per_assigner_group"]
    assert m["model"]["hc_capture_at_k"]["overall"] >= t["hc_capture_at_k"]["overall"]
    assert crit["overall"] - m["v0"]["critical_capture_at_k"]["overall"] >= t["beat_v0_by"]