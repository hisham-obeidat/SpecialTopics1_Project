"""Pipeline step 1: check the raw data against features.yaml."""
import pandas as pd

from cve_triage.config import all_columns


class DataValidationError(ValueError):
    """Raised when a data file does not match features.yaml."""


def validate_dataframe(df, spec, require_label=True):
    expected = all_columns(spec)
    if not require_label:
        expected = [c for c in expected if c != spec["label"]]
    missing = sorted(set(expected) - set(df.columns))
    unexpected = sorted(set(df.columns) - set(expected))
    if missing or unexpected:
        raise DataValidationError(
            f"Columns do not match features.yaml. Missing: {missing}. Unexpected: {unexpected}."
        )
    if df.empty:
        raise DataValidationError("The data file has no rows.")

    id_col, time_col, label = spec["id"], spec["time"], spec["label"]
    if df[id_col].isna().any() or df[id_col].duplicated().any():
        raise DataValidationError(f"Column '{id_col}' has empty or duplicate values.")

    times = pd.to_datetime(df[time_col], utc=True, errors="coerce")
    if times.isna().any():
        bad = df.loc[times.isna(), id_col].head(5).tolist()
        raise DataValidationError(f"Column '{time_col}' has values that are not dates, e.g. rows {bad}.")

    if require_label:
        allowed = {"LOW", "MEDIUM", "HIGH", "CRITICAL"}
        bad_labels = set(df[label].dropna().unique()) - allowed
        if df[label].isna().any() or bad_labels:
            raise DataValidationError(
                f"Column '{label}' must be one of {sorted(allowed)}; found {sorted(bad_labels)} or empty values."
            )

    df = df.copy()
    df[time_col] = times
    return df


def validate_file(path, spec, require_label=True):
    try:
        df = pd.read_csv(path, dtype=str, keep_default_na=False, na_values=[""])
    except Exception as exc:
        raise DataValidationError(f"Cannot read {path}: {exc}") from exc
    for col in spec["features"].get("numeric") or []:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    return validate_dataframe(df, spec, require_label=require_label)