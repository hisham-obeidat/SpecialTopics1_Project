"""Pipeline step 2: build the feature transformer from features.yaml only."""
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import FunctionTransformer, StandardScaler


def split_semicolon(value):
    """Tokenizer for categorical columns: 'CWE-79;CWE-89' -> ['CWE-79', 'CWE-89']."""
    return [v.strip() for v in value.split(";") if v.strip()]


def select_features(df, text=(), categorical=(), numeric=()):
    """Keep only feature columns and fill missing values. No other column passes."""
    out = pd.DataFrame(index=df.index)
    for col in list(text) + list(categorical):
        values = df[col] if col in df.columns else pd.Series("", index=df.index)
        out[col] = values.fillna("").astype(str)
    for col in numeric:
        values = df[col] if col in df.columns else pd.Series(np.nan, index=df.index)
        out[col] = pd.to_numeric(values, errors="coerce")
    return out


def build_transformer(spec, tfidf_params=None):
    f = spec["features"]
    text = list(f.get("text") or [])
    categorical = list(f.get("categorical") or [])
    numeric = list(f.get("numeric") or [])
    tfidf_params = dict(tfidf_params or {})
    if "ngram_range" in tfidf_params:
        tfidf_params["ngram_range"] = tuple(tfidf_params["ngram_range"])

    parts = []
    for col in text:
        parts.append((f"text_{col}", TfidfVectorizer(sublinear_tf=True, **tfidf_params), col))
    for col in categorical:
        # Values never seen in training are simply ignored at prediction time.
        parts.append((f"cat_{col}", CountVectorizer(tokenizer=split_semicolon, lowercase=False,
                                                    token_pattern=None, binary=True), col))
    if numeric:
        parts.append(("num", Pipeline([
            ("impute", SimpleImputer(strategy="median")),
            ("log", FunctionTransformer(np.log1p)),
            ("scale", StandardScaler()),
        ]), numeric))

    return Pipeline([
        ("select", FunctionTransformer(select_features, kw_args={
            "text": text, "categorical": categorical, "numeric": numeric})),
        ("columns", ColumnTransformer(parts, sparse_threshold=1.0)),
    ])