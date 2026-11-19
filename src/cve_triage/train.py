"""Pipeline step 3: train the classifier on the training split."""
import joblib
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline

from cve_triage.features import build_transformer


def build_model(spec, cfg):
    m = cfg["model"]
    clf = LogisticRegression(random_state=m.get("random_state", 42), **m["params"])
    return Pipeline([
        ("features", build_transformer(spec, m.get("tfidf"))),
        ("clf", clf),
    ])


def train_model(train_df, spec, cfg):
    model = build_model(spec, cfg)
    model.fit(train_df, train_df[spec["label"]])
    return model


def predict_proba(model, df):
    """Return (P(CRITICAL), P(HIGH)) for every row."""
    proba = model.predict_proba(df)
    classes = list(model.classes_)
    return proba[:, classes.index("CRITICAL")], proba[:, classes.index("HIGH")]


def save_model(model, path):
    joblib.dump(model, path)


def load_model(path):
    return joblib.load(path)