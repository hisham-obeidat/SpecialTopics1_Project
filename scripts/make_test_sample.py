"""Make the small test sample in tests/data/ from the full history (about 200 rows).

Usage: python scripts/make_test_sample.py data/cves_history.csv tests/data/sample.csv
"""
import sys

import pandas as pd
import yaml

src, dst = sys.argv[1], sys.argv[2]
spec = yaml.safe_load(open("features.yaml", encoding="utf-8"))
label, time, id_col = spec["label"], spec["time"], spec["id"]
df = pd.read_csv(src, dtype=str, keep_default_na=False)
df = df[df[time] >= "2025-05-01"]          # 8 months: enough for train / validation / test
month = df[time].str[:7]

# 6 CVEs of each severity per month, so every split has every class
shuffled = df.sample(frac=1, random_state=0)
parts = [shuffled.groupby([month, shuffled[label]]).head(6)]
# extra edge cases for the never-wait rule
cwes = df["cwe_ids"].str.split(";")
parts.append(df[cwes.apply(lambda c: bool({"CWE-78", "CWE-94", "CWE-287", "CWE-306", "CWE-502"} & set(c)))].sample(10, random_state=0))
parts.append(df[cwes.apply(lambda c: "CWE-787" in c)].sample(5, random_state=0))

out = pd.concat(parts)
out = out[~out.index.duplicated()].sort_values([time, id_col])
out.to_csv(dst, index=False)
print(f"{len(out)} rows written to {dst}")