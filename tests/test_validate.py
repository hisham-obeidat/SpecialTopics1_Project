import pytest

from tests.conftest import SAMPLE
from cve_triage.validate import DataValidationError, validate_file


def test_missing_column_stops_with_clear_error(tmp_path, spec, sample):
    broken = tmp_path / "broken.csv"
    sample.drop(columns=[spec["features"]["text"][0]]).to_csv(broken, index=False)
    with pytest.raises(DataValidationError, match="Missing"):
        validate_file(broken, spec)


def test_unexpected_column_stops(tmp_path, spec, sample):
    broken = tmp_path / "broken.csv"
    sample.assign(extra=1).to_csv(broken, index=False)
    with pytest.raises(DataValidationError, match="Unexpected"):
        validate_file(broken, spec)


def test_bad_date_stops(tmp_path, spec, sample):
    broken = tmp_path / "broken.csv"
    df = sample.copy()
    df[spec["time"]] = df[spec["time"]].astype(str)
    df.loc[df.index[0], spec["time"]] = "not a date"
    df.to_csv(broken, index=False)
    with pytest.raises(DataValidationError, match="not dates"):
        validate_file(broken, spec)


def test_valid_sample_passes(spec):
    assert len(validate_file(SAMPLE, spec)) > 100