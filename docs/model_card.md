\# Model card: CVE Triage Assistant (cve-triage, version 2)



\*\*Intended use.\*\* Orders each day's new CVEs so Haris Security's analysts review the most severe first, within a capacity of K = 40 per day. The score is the model's probability that a CVE is Critical. It is an estimate for prioritization only. It is \*\*not\*\* a CVSS score and must not replace one. The model never hides or closes a CVE. CVEs with a never-wait weakness (CWE-78, 94, 287, 306, 502) always come first.



\*\*Model.\*\* TF-IDF (words and word pairs) on the description, plus one-hot encodings of assigner, assigner group, vendor, product and CWE IDs, and log-scaled counts of affected products and references. These go into a 4-class logistic regression (C = 1.0, balanced class weights). No LLMs and no pretrained embeddings are used. Only columns known at publication time are features (see `features.yaml`).



\*\*Data windows\*\* (split by time, never shuffled):

\- Training: 2024-01-01 to 2025-08-31 (63,906 CVEs)

\- Validation: 2025-09-01 to 2025-10-31 (6,750 CVEs). Used to choose C, from 0.3, 1.0 and 3.0.

\- Test: 2025-11-01 to 2025-12-31 (6,726 CVEs after removing 49 whose description duplicates a training CVE). Used once, for the final numbers.



\*\*Labels.\*\* `severity` comes from the CVSS v3 score given by the publisher (CNA) or by CISA. All of the data comes from the public CVE List (CVEProject/cvelistV5).



\*\*Results on the test set\*\* (K = 40, 61 days, 16 of which have 40 CVEs or fewer):



| Metric | v0 (publication order) | Model |

|---|---|---|

| Critical-capture@K, overall | 0.419 | 0.767 |

| Critical-capture@K, top10 publishers | 0.551 | 0.771 |

| Critical-capture@K, other publishers | 0.133 | 0.757 |

| HC-capture@K, overall | 0.309 | 0.416 |

| Recall of the Critical class | | 0.665 |



All targets in `config.yaml` are met.



\*\*Known limitations.\*\*

\- The history holds only CVEs that received a score. CVEs that are never scored may look different.

\- Since April 2026, NIST scores far fewer CVEs, so future labels come mostly from publishers. Their scoring habits differ, and the model learns them.

\- The text model can be fooled by unusual wording, and it doesn't see exploit information.

\- The "other" assigner group is small and mixed, so its results vary more from month to month.

\- On days with 40 CVEs or fewer, every CVE is captured, which inflates capture rates.

