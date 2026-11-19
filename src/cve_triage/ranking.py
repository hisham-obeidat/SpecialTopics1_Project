"""Never-wait rule, model ranking rule and v0 baseline."""
import numpy as np
import pandas as pd

NEVER_WAIT_CWES = frozenset({"CWE-78", "CWE-94", "CWE-287", "CWE-306", "CWE-502"})
CWE_COLUMN = "cwe_ids"  # the only column name allowed outside features.yaml


def never_wait_cwes(cwe_ids):
    """Never-wait CWEs in a ';'-separated string. Compares whole IDs, so CWE-787 is not CWE-78."""
    if not isinstance(cwe_ids, str):
        return []
    found = {c.strip().upper() for c in cwe_ids.split(";")} & NEVER_WAIT_CWES
    return sorted(found)


def is_never_wait(cwe_ids):
    return len(never_wait_cwes(cwe_ids)) > 0


def _finish(ordered, spec, score):
    return pd.DataFrame({
        spec["id"]: ordered[spec["id"]].to_numpy(),
        "rank": np.arange(1, len(ordered) + 1),
        "score": score,
    })


def rank_day(day, p_critical, p_high, spec):
    """Order one day: never-wait first, then the rest. Inside each group:
    P(CRITICAL) desc, then P(HIGH) desc, then publication time asc, then cve_id asc."""
    id_col, time_col = spec["id"], spec["time"]
    work = pd.DataFrame({
        "_nw": [0 if is_never_wait(c) else 1 for c in day[CWE_COLUMN]],
        "_crit": np.asarray(p_critical, dtype=float),
        "_high": np.asarray(p_high, dtype=float),
        time_col: pd.to_datetime(day[time_col], utc=True).to_numpy(),
        id_col: day[id_col].to_numpy(),
    })
    ordered = work.sort_values(["_nw", "_crit", "_high", time_col, id_col],
                               ascending=[True, False, False, True, True], kind="mergesort")
    return _finish(ordered, spec, ordered["_crit"].to_numpy())


def rank_v0(day, spec):
    """Today's rule v0: publication time (oldest first), ties broken by cve_id."""
    id_col, time_col = spec["id"], spec["time"]
    work = pd.DataFrame({
        time_col: pd.to_datetime(day[time_col], utc=True).to_numpy(),
        id_col: day[id_col].to_numpy(),
    })
    ordered = work.sort_values([time_col, id_col], kind="mergesort")
    return _finish(ordered, spec, np.full(len(ordered), np.nan))