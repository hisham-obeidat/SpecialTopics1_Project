# Evaluation on the test set

- K per day: 40
- Test CVEs: 6726 over 61 days
- Test days with K CVEs or fewer: 16
- Test CVEs removed as duplicates of training: 49
- Recall of the Critical class: 0.703

## Critical-capture@K

| Slice | v0 | Model |
|---|---|---|
| Overall | 0.419 | 0.747 |
| assigner_group = other | 0.133 | 0.769 |
| assigner_group = top10 | 0.551 | 0.737 |

## HC-capture@K

| Slice | v0 | Model |
|---|---|---|
| Overall | 0.309 | 0.412 |
| assigner_group = other | 0.120 | 0.427 |
| assigner_group = top10 | 0.390 | 0.406 |
