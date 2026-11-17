# Paper-inspired urinalysis experiments

## What was implemented

Each cohort was trained and evaluated separately using three fixed classifiers,
one inspired by each paper in `papers/`. These are **adaptations, not
reproductions** of the published results: the papers use different cohorts,
features, outcome definitions, training protocols and/or hyperparameters.
The trained models here are not the authors' original models.

| Paper | Approach used here | Important differences |
| --- | --- | --- |
| [Dedeene et al. (2024)](https://doi.org/10.1016/j.cca.2024.119854) | Multilayer perceptron (MLP), hidden layers 32 and 16 | The paper used more features, grid search, time-separated test sets and likelihood-ratio categories; none are reproduced here. |
| [Farashi and Momtaz (2025)](https://doi.org/10.1186/s12911-024-02819-2) | Soft-voting ensemble of XGBoost, decision tree and LightGBM | The paper used a larger set of urine, blood and demographic features, feature selection and tuning. The equal-weight soft vote and fixed parameters here are implementation choices, not necessarily the paper's voting details. |
| [Favresse et al. (2025)](https://doi.org/10.1093/clinchem/hvaf088) | CatBoost classifier | The paper used dipstick reflectance, demographics and five UTI definitions. Here fixed settings and the available binary label are used. |

## Data and procedure

- **Dataset 1:** `urinalysis_tests.csv` has 1,436 records, 81 positive labels,
  and 14 predictors. The source and definition of `Diagnosis` are not
  documented in this repository. The index and label are excluded from inputs.
- **Dataset 2:** FlowUTI has separate elderly (1,174 records, 496 positives)
  and neonatal (204 records, 57 positives) files. We do not pool them because
  age populations, instruments and culture positivity thresholds differ.
  See [`data/flowuti/README.md`](../data/flowuti/README.md) for provenance.
  Both have only bacteria and leukocyte measurements and a culture label;
  this outcome and these measures are not necessarily equivalent to those in
  dataset 1. The original and FlowUTI datasets are not schema-compatible for
  direct external testing without further harmonization.
- For each cohort, use five-fold stratified group splitting (seed 42) and
  select the fold whose positive prevalence is closest to the whole cohort as
  the roughly 20% holdout. This choice uses labels but **not model scores or
  test performance**. Exact duplicate feature vectors are grouped so that they
  cannot cross the split, even where they have different labels. Patient IDs
  are unavailable, so patient-level independence cannot be guaranteed.
- Numeric predictors are median-imputed and standardized; categorical
  predictors, including WBC/RBC ranges, are mode-imputed and one-hot encoded.
  Unknown categories are ignored. The imputer, scaler and encoder are fitted
  only on training data. All methods use the same features and split within
  each cohort. There is no feature selection, hyperparameter search, threshold
  tuning, resampling, or separate external/temporal validation.
- Predict positive when probability is **at least 0.5**. This default threshold
  has not been selected for clinical sensitivity. AP is average precision
  (a precision–recall summary); ROC AUC and AP use probabilities, while
  accuracy, precision, recall and specificity use the 0.5 threshold. An
  all-negative classifier provides a baseline; its precision is reported as 0
  by convention because it predicts no positives.

## Held-out results

Values rounded to three decimals. FN is the number of positive samples missed.
Full precision, confusion matrices and baseline results are in
[`metrics.csv`](metrics.csv); split details are in [`splits.json`](splits.json).

| Cohort (test size; positives) | Method | ROC AUC | AP | Accuracy | Precision | Recall | Specificity | FN |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Original (286; 14) | Dedeene-inspired MLP | 0.718 | 0.267 | 0.944 | 0.400 | 0.286 | 0.978 | 10 |
| Original (286; 14) | Farashi-inspired voting | 0.807 | 0.356 | 0.951 | 0.500 | 0.071 | 0.996 | 13 |
| Original (286; 14) | Favresse-inspired CatBoost | 0.783 | 0.341 | 0.958 | 1.000 | 0.143 | 1.000 | 12 |
| Elderly (232; 98) | Dedeene-inspired MLP | 0.925 | 0.920 | 0.853 | 0.900 | 0.735 | 0.940 | 26 |
| Elderly (232; 98) | Farashi-inspired voting | 0.924 | 0.923 | 0.858 | 0.835 | 0.827 | 0.881 | 17 |
| Elderly (232; 98) | Favresse-inspired CatBoost | 0.905 | 0.903 | 0.862 | 0.851 | 0.816 | 0.896 | 18 |
| Neonates (42; 12) | Dedeene-inspired MLP | 0.919 | 0.832 | 0.786 | 0.667 | 0.500 | 0.900 | 6 |
| Neonates (42; 12) | Farashi-inspired voting | 0.867 | 0.742 | 0.786 | 0.667 | 0.500 | 0.900 | 6 |
| Neonates (42; 12) | Favresse-inspired CatBoost | 0.881 | 0.762 | 0.786 | 0.667 | 0.500 | 0.900 | 6 |

On dataset 1, predicting every case negative achieves 95.1% accuracy and
misses all 14 positives. At the chosen threshold all three models also miss
most positives; CatBoost's apparent 100% precision comes from just two positive
predictions. AUC can be high while threshold-specific recall is poor. The
neonatal holdout contains only 12 positives, making its estimates especially
unstable. These are single-split exploratory estimates, not evidence that one
method is generally superior; results may vary substantially with the split.
Different labels, populations and prevalence also make cross-dataset score
comparisons misleading. No clinical decisions should be based on these models.
For a stronger study, establish label provenance, obtain patient IDs, perform
patient-level and external/temporal validation, quantify uncertainty, and choose
and calibrate any clinical threshold using training/validation data only.

## Reproduce

From the repository root, using Python 3.11:

```sh
python -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
python -m unittest discover -s tests -v
python experiments/run_experiments.py
```

The script overwrites `results/metrics.csv` and `results/splits.json`. Seeds,
model settings, preprocessing and splitting are defined in the script. Small
numerical differences may occur across platforms.
