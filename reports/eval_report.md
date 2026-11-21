# Evaluation on the test set

- K per day: 40
- Test CVEs: 6726 over 61 days
- Test days with K CVEs or fewer: 16
- Test CVEs removed as duplicates of training: 49
- Recall of the Critical class: 0.645

## Critical-capture@K

| Slice | v0 | Model |
|---|---|---|
| Overall | 0.419 | 0.750 |
| assigner_group = other | 0.133 | 0.763 |
| assigner_group = top10 | 0.551 | 0.745 |

## HC-capture@K

| Slice | v0 | Model |
|---|---|---|
| Overall | 0.309 | 0.413 |
| assigner_group = other | 0.120 | 0.422 |
| assigner_group = top10 | 0.390 | 0.408 |