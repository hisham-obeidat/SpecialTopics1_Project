"""Pipeline step 4: evaluate the model and v0, write reports."""
import json
from pathlib import Path

from sklearn.metrics import recall_score

from cve_triage.metrics import day_key, ranks_per_day, summarize
from cve_triage.ranking import rank_day, rank_v0
from cve_triage.train import predict_proba


def evaluate(model, test_df, spec, k, n_duplicates_removed=0):
    p_crit, p_high = predict_proba(model, test_df)
    test_df = test_df.assign(_p_crit=p_crit, _p_high=p_high)

    model_ranks = ranks_per_day(test_df, spec,
                                lambda d: rank_day(d, d["_p_crit"], d["_p_high"], spec))
    v0_ranks = ranks_per_day(test_df, spec, lambda d: rank_v0(d, spec))

    day_sizes = test_df.groupby(day_key(test_df, spec)).size()
    pred = model.predict(test_df)
    return {
        "k_per_day": k,
        "n_test_cves": int(len(test_df)),
        "n_test_days": int(len(day_sizes)),
        "n_days_with_k_or_fewer": int((day_sizes <= k).sum()),
        "n_test_duplicates_removed": int(n_duplicates_removed),
        "critical_recall": float(recall_score(test_df[spec["label"]], pred,
                                              labels=["CRITICAL"], average="macro")),
        "model": summarize(test_df, model_ranks, spec, k),
        "v0": summarize(test_df, v0_ranks, spec, k),
    }


def _fmt(x):
    return "n/a" if x is None else f"{x:.3f}"


def write_reports(metrics, reports_dir, title="Evaluation on the test set"):
    reports_dir = Path(reports_dir)
    reports_dir.mkdir(parents=True, exist_ok=True)
    (reports_dir / "metrics.json").write_text(json.dumps(metrics, indent=2), encoding="utf-8")

    k = metrics["k_per_day"]
    lines = [f"# {title}", "",
             f"- K per day: {k}",
             f"- Test CVEs: {metrics['n_test_cves']} over {metrics['n_test_days']} days",
             f"- Test days with K CVEs or fewer: {metrics['n_days_with_k_or_fewer']}",
             f"- Test CVEs removed as duplicates of training: {metrics['n_test_duplicates_removed']}",
             f"- Recall of the Critical class: {_fmt(metrics['critical_recall'])}", ""]
    for name, key in [("Critical-capture@K", "critical_capture_at_k"), ("HC-capture@K", "hc_capture_at_k")]:
        m, v = metrics["model"][key], metrics["v0"][key]
        lines += [f"## {name}", "", "| Slice | v0 | Model |", "|---|---|---|",
                  f"| Overall | {_fmt(v['overall'])} | {_fmt(m['overall'])} |"]
        for slice_key in [s for s in m if s.startswith("by_")]:
            for g in sorted(m[slice_key]):
                lines.append(f"| {slice_key[3:]} = {g} | {_fmt(v[slice_key].get(g))} | {_fmt(m[slice_key][g])} |")
        lines.append("")
    (reports_dir / "eval_report.md").write_text("\n".join(lines), encoding="utf-8")