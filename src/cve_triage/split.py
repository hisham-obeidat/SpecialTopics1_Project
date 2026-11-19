"""Time split and duplicate removal. Never shuffles."""
import re

CVE_ID_PATTERN = re.compile(r"cve-\d{4}-\d+")
WHITESPACE = re.compile(r"\s+")


def normalize_description(text):
    """Lowercase, remove CVE IDs, collapse white space."""
    if not isinstance(text, str):
        return ""
    text = CVE_ID_PATTERN.sub(" ", text.lower())
    return WHITESPACE.sub(" ", text).strip()


def time_split(df, spec, test_months=2, validation_months=2):
    """Split by calendar month: test = last `test_months` months,
    validation = the `validation_months` months before, train = everything earlier."""
    times = df[spec["time"]]
    last_month = times.max().tz_convert(None).to_period("M")
    test_start = (last_month - (test_months - 1)).to_timestamp().tz_localize("UTC")
    val_start = (last_month - (test_months + validation_months - 1)).to_timestamp().tz_localize("UTC")

    train = df[times < val_start]
    val = df[(times >= val_start) & (times < test_start)]
    test = df[times >= test_start]
    return train.copy(), val.copy(), test.copy()


def remove_duplicates(test, train, spec):
    """Drop test rows whose normalized description also appears in train.
    Returns (filtered_test, number_removed)."""
    text_col = spec["features"]["text"][0]
    seen = set(train[text_col].map(normalize_description))
    is_dup = test[text_col].map(normalize_description).isin(seen)
    return test[~is_dup].copy(), int(is_dup.sum())