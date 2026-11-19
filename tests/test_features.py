import numpy as np

from cve_triage.config import feature_columns
from cve_triage.train import predict_proba


def test_handles_empty_description_missing_cwe_unknown_vendor(trained, sample, spec):
    row = sample.iloc[[0]].copy()
    row[spec["features"]["text"][0]] = ""
    row["cwe_ids"] = np.nan
    for col in spec["features"]["categorical"]:
        if col != "cwe_ids":
            row[col] = "never-seen-before-value"
    p_crit, p_high = predict_proba(trained, row)
    assert 0.0 <= p_crit[0] <= 1.0 and 0.0 <= p_high[0] <= 1.0


def test_changing_non_feature_columns_leaves_predictions_unchanged(trained, sample, spec):
    before = trained.predict_proba(sample)
    changed = sample.copy()
    for col in changed.columns:
        if col in feature_columns(spec):
            continue
        changed[col] = "changed" if changed[col].dtype == object else 0
    after = trained.predict_proba(changed)
    assert np.allclose(before, after)