"""Critical-capture@K and HC-capture@K, for any ranking function."""
import pandas as pd


def day_key(df, spec):
    return pd.to_datetime(df[spec["time"]], utc=True).dt.date


def capture_at_k(df, ranks, spec, k, classes, group_col=None):
    """Captured / total for the given label classes, summed over all days.
    `ranks` is a Series aligned with df: rank of each CVE inside its own day."""
    target = df[spec["label"]].isin(classes)
    captured = target & (ranks <= k)
    if group_col is None:
        total = int(target.sum())
        return float(captured.sum() / total) if total else None
    out = {}
    for g, idx in df.groupby(group_col).groups.items():
        total = int(target.loc[idx].sum())
        out[str(g)] = float(captured.loc[idx].sum() / total) if total else None
    return out


def ranks_per_day(df, spec, rank_fn):
    """Apply rank_fn(day_df) to each day and return each row's rank, aligned with df."""
    id_col = spec["id"]
    ranks = pd.Series(index=df.index, dtype=float)
    for _, day in df.groupby(day_key(df, spec)):
        ranked = rank_fn(day)
        rank_by_id = dict(zip(ranked[id_col], ranked["rank"]))
        ranks.loc[day.index] = day[id_col].map(rank_by_id).to_numpy()
    return ranks


def summarize(df, ranks, spec, k):
    res = {
        "critical_capture_at_k": {"overall": capture_at_k(df, ranks, spec, k, ["CRITICAL"])},
        "hc_capture_at_k": {"overall": capture_at_k(df, ranks, spec, k, ["HIGH", "CRITICAL"])},
    }
    for g in spec.get("groups") or []:
        res["critical_capture_at_k"][f"by_{g}"] = capture_at_k(df, ranks, spec, k, ["CRITICAL"], g)
        res["hc_capture_at_k"][f"by_{g}"] = capture_at_k(df, ranks, spec, k, ["HIGH", "CRITICAL"], g)
    return res