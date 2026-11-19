import pandas as pd

from tests.conftest import SAMPLE
from cve_triage.config import all_columns, feature_columns

LABEL_COLUMNS = {"severity", "cvss_score", "cvss_vector", "score_source", "scored_at"}


def test_every_column_has_exactly_one_role(spec):
    data_cols = list(pd.read_csv(SAMPLE, nrows=1).columns)
    roles = all_columns(spec)
    assert len(roles) == len(set(roles)), "a column appears in more than one role"
    assert sorted(roles) == sorted(data_cols)


def test_no_label_column_is_a_feature(spec):
    assert not set(feature_columns(spec)) & LABEL_COLUMNS
    for col, reason in spec["not_features"].items():
        assert isinstance(reason, str) and reason.strip(), f"{col} needs a reason"


def test_groups_have_a_role(spec):
    for g in spec["groups"]:
        assert g in all_columns(spec)