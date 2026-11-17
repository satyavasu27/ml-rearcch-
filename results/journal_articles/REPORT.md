# Three journal-paper-inspired methods on two selected datasets

## Selected journal papers

These are original journal research articles, not conference papers. The
implementations below use selected algorithm families, **not** the authors'
trained models or full protocols. Results are exploratory, not clinical tools.

1. **Choi MH, Kim D, Park Y, Jeong SH.** Development and validation of
   artificial intelligence models to predict urinary tract infections and
   secondary bloodstream infections in adult patients. *Journal of Infection
   and Public Health*, 17(1), 10–17 (2024; online 2023).
   [DOI](https://doi.org/10.1016/j.jiph.2023.10.021). Compared TabNet, KNN,
   LightGBM and XGBoost on 259,187 hospital patients, with separate hospital
   validation; XGBoost reported external AUROC 0.967 for its UTI/culture outcome
   and 0.955 for UT-related bloodstream infection. **Our adaptation:** a fixed
   XGBoost classifier for culture positivity only. We do not have the original
   predictors, outcome definitions, model settings, external hospital or a
   UT-BSI label; we do not implement or assess UT-BSI prediction.
2. **Sheele JM, Campbell RL, Jones DD.** Machine learning to predict
   bacteriuria in the emergency department. *Scientific Reports* 15, 31087
   (2025). [DOI](https://doi.org/10.1038/s41598-025-16677-z). Studied 62,963
   encounters, using several algorithms including random forest and XGBoost for
   different culture-growth thresholds. The reported best XGBoost AUROC was
   0.931 for ≥100,000 CFU/mL. **Our adaptation:** a fixed random forest, one of
   the evaluated algorithm families, not the paper's best XGBoost model. We
   lack the original clinical history, multiple outcome thresholds and protocol.
3. **Sergounioti A, Rigas D, Zoitopoulos V, Kalles D.** From Preliminary
   Urinalysis to Decision Support: Machine Learning for UTI Prediction in
   Real-World Laboratory Data. *Journal of Personalized Medicine* 15(5), 200
   (2025). [DOI](https://doi.org/10.3390/jpm15050200). Tested five ensemble
   methods on 8,065 samples; XGBoost achieved AUROC 0.819. Their soft-voting
   classifier combined random forest, XGBoost and extra trees. **Our adaptation:**
   equal-weight soft voting of those three classifier types. We do not reproduce
   their balanced-bagging framework, 10-fold CV, tuning or threshold selection.
   Note: these authors differ from the names listed in the request; the names
   here follow the linked article.

## Data sources, distinct from those three method papers

- **Taylor et al.** (PLOS ONE, 2018): 80,387 actual ED visits, 55,365
  patients, `UCX_abnormal` target. [Original study](https://doi.org/10.1371/journal.pone.0194085),
  [dataset source](https://plos.figshare.com/articles/dataset/Predicting_urinary_tract_infections_in_the_emergency_department_with_machine_learning/5959417),
  [local provenance](../../data/taylor/README.md). Available locally, checked
  against publisher checksum, and evaluated below.
- **Trang et al.** (PLOS ONE, 2025): original study reports a discovery
  cohort of 2,617 symptomatic adult outpatients, with urinalysis, urine flow
  cytometry and a culture-derived case/control label. [Original study](https://doi.org/10.1371/journal.pone.0323664),
  [public discovery CSV](https://pmc.ncbi.nlm.nih.gov/articles/instance/12077719/bin/pone.0323664.s003.csv).
  **Not in the checkout:** this environment cannot download from the publisher
  host. Its count and contents remain unverified locally and no results have
  been generated. Download and upload this file to proceed.

Culture positivity is not equivalent to clinical UTI. The populations, lab
measurements, and outcome definitions differ across these studies. Neither
chosen dataset supplies the label needed to evaluate Choi's UT-BSI task.

## Experimental procedure

All three adaptations use the same predeclared predictors, target, and test
partition per dataset, plus an all-negative baseline. On Taylor the predictor
set is age, gender and 16 available urinalysis measures; we omit patient IDs,
diagnosis/disposition/antibiotics, culture results and variables of uncertain
availability. `not_reported` is retained as a category. Numeric features use
training-set median imputation and scaling; categorical features use training-set
mode imputation and one-hot encoding. The split is a seed-42 80/20 patient-group
shuffle using `PATID`, so no patient appears in both partitions. This is neither
temporal nor independent external validation. There may still be timing issues.

Trang support is **preliminary and unverified against the actual file**. It
selects sex and prespecified urinalysis/flow-cytometry fields and excludes the
culture organism and culture target from predictors. It treats nonnumeric
entries such as `MS` as missing. Validate the file, coding, variable dictionary,
label definition and exclusions before use. Its intended stratified record split
cannot establish patient independence if patient IDs are unavailable. Do not
interpret results as cross-site validation: the cohorts, measurements and
outcomes differ. No models are trained across both datasets.

Threshold is 0.5 with no tuning. AUROC and average precision (AP) use predicted
probabilities; recall, specificity and false negatives use the threshold. There
is no confidence interval, calibration, model tuning, or prospective validation.
The settings are implementation choices; see `experiments/run_selected.py`.

## Results: Taylor only

Training: 64,336 visits, 14,659 positive. Holdout: 16,051 visits, 3,625 positive.

| Approach | AUROC | AP | Recall | Specificity | False negatives |
| --- | ---: | ---: | ---: | ---: | ---: |
| All-negative baseline | 0.500 | 0.226 | 0.000 | 1.000 | 3,625 |
| Choi-inspired XGBoost | 0.891 | 0.763 | 0.543 | 0.956 | 1,658 |
| Sheele-inspired random forest | 0.892 | 0.765 | 0.544 | 0.960 | 1,652 |
| Sergounioti-inspired voting | 0.894 | 0.768 | 0.544 | 0.960 | 1,652 |

Full metrics are in `taylor_metrics.csv`; split and feature details in
`taylor_split.json`. Many positives are missed at this untuned threshold. These
are not the original paper results and must not be used for clinical decisions.

## Reproduce

Install `requirements.txt` in a Python 3.11 environment. From the repository root:

```sh
python -m unittest discover -s tests -v
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 python experiments/run_selected.py --dataset taylor
```

Upload the Trang discovery CSV as `data/trang/pone.0323664.s003.csv`, verify its
source and fields, then run `python experiments/run_selected.py --dataset trang`.
The default `--dataset all` requires both files and errors before training if
either is missing. Each run writes separate dataset outputs in this directory.
