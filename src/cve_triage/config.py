"""Load features.yaml and config.yaml."""
import yaml


def load_yaml(path):
    with open(path, encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def load_features(path="features.yaml"):
    return load_yaml(path)


def load_config(path="config.yaml"):
    return load_yaml(path)


def feature_columns(spec):
    """All feature columns, in a fixed order: text, categorical, numeric."""
    f = spec["features"]
    return list(f.get("text") or []) + list(f.get("categorical") or []) + list(f.get("numeric") or [])


def all_columns(spec):
    """Every column named in features.yaml."""
    return [spec["label"], spec["id"], spec["time"]] + feature_columns(spec) + list(spec.get("not_features") or {})