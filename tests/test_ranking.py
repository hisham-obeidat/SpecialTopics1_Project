import pandas as pd

from cve_triage.ranking import is_never_wait, rank_day, rank_v0


def make_day():
    return pd.DataFrame({
        "cve_id": ["CVE-2025-0004", "CVE-2025-0002", "CVE-2025-0003", "CVE-2025-0001"],
        "published_at": ["2025-01-01T01:00Z", "2025-01-01T00:00Z", "2025-01-01T02:00Z", "2025-01-01T00:00Z"],
        "cwe_ids": ["CWE-787", "CWE-78;CWE-79", None, ""],
    })


def test_never_wait_matches_whole_ids_only():
    assert is_never_wait("CWE-79;CWE-502")
    assert not is_never_wait("CWE-787")
    assert not is_never_wait("")
    assert not is_never_wait(None)


def test_never_wait_first_then_by_score(spec):
    ranked = rank_day(make_day(), [0.9, 0.1, 0.2, 0.5], [0, 0, 0, 0], spec)
    order = ranked["cve_id"].tolist()
    assert order[0] == "CVE-2025-0002"   # CWE-78 is never-wait, despite its low score
    assert order[1:] == ["CVE-2025-0004", "CVE-2025-0001", "CVE-2025-0003"]  # CWE-787 and empty: by score
    assert ranked["rank"].tolist() == [1, 2, 3, 4]


def test_ties_broken_by_high_then_time_then_id(spec):
    ranked = rank_day(make_day(), [0.5, 0.5, 0.5, 0.5], [0.1, 0.0, 0.1, 0.1], spec)
    assert ranked["cve_id"].tolist() == ["CVE-2025-0002", "CVE-2025-0001", "CVE-2025-0004", "CVE-2025-0003"]


def test_v0_orders_by_time_then_cve_id(spec):
    ranked = rank_v0(make_day(), spec)
    assert ranked["cve_id"].tolist() == ["CVE-2025-0001", "CVE-2025-0002", "CVE-2025-0004", "CVE-2025-0003"]