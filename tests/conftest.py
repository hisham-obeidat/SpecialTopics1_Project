from pathlib import Path

import pytest
import yaml

from cve_triage.config import load_config, load_features
from cve_triage.validate import validate_file

ROOT = Path(__file__).resolve().parents[1]
SAMPLE = ROOT / "tests" / "data" / "sample.csv"


@pytest.fixture(scope="session")
def spec():
    return load_features(ROOT / "features.yaml")


@pytest.fixture(scope="session")
def cfg():
    return load_config(ROOT / "config.yaml")


@pytest.fixture(scope="session")
def sample(spec):
    return validate_file(SAMPLE, spec)


@pytest.fixture(scope="session")
def small_cfg(cfg):
    """Same settings, but TF-IDF min_df=1 so the tiny sample has a vocabulary."""
    c = yaml.safe_load(yaml.safe_dump(cfg))
    c["model"]["tfidf"]["min_df"] = 1
    return c


@pytest.fixture(scope="session")
def trained(sample, spec, small_cfg):
    from cve_triage.train import train_model
    return train_model(sample, spec, small_cfg)